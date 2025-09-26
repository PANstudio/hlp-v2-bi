(() => {

	/* ---
	| PREP
	--- */

	//report for duty
	console.log('HLP SS custom JS loaded');

	//global namespace for e.g. map charts hooks
	window.hlp = {};

	//domains
	const hlpDomains = ['https://hlpst.app', 'https://hlp.city', 'http://localhost:1906', 'https://stage.hlpst.app'];

	/* ---
	| MESSAGES - listen for messages from HLP parent - must have an `id` property denoting message ID - see 
	--- */

	let hlpDomain;
	addEventListener('message', evt => {
		if (!hlpDomains.includes(evt.origin)) return;
		switch (evt.data.id) {

			//report domain - parent reports domain and we repeatedly respond with content height, for frame sizing
			case 'report-domain':
				hlpDomain = evt.data.domain;
				setInterval(
					() => parent.postMessage({id: 'report-height', height: document.body.scrollHeight}, evt.data.domain),
					2000
				);
				break;
		}
	});

	/* ---
	| MAP CHARTS CUSTOM JS - see https://t.ly/MMVEy
	--- */

	hlp.mapsCustomJs = {
		tooltip: () => ctx => `${ctx.object.extraProps.agent_name} (${ctx.object.extraProps.total})`,
		click: () => ctx => `https://${subDomain(ctx)}hlpst.app/agent/${ctx.object.extraProps.agent}/conversation?db=${db(ctx)}`
	};

	//utils for chart JS
	const subDomain = ctx => !['stage', 'dev'].includes(db(ctx)) ? '' : db(ctx)+'.';
	const db = ctx => ctx.object.extraProps.db;

	/* ---
	| DASHBOARD TWEAKS
	--- */

	//make busiest day/hour charts show text (something big number charts can't natively do). Need to interval this as
	//we can't know when a chart has rendered
	setInterval(() => {
	    const dayEl = document.querySelector('[data-test-chart-name="Convos - busiest day"] .superset-legacy-chart-big-number div')
	    const dayNum = parseInt(dayEl?.textContent);
	    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
	    if (dayEl && dayNum) dayEl.textContent = days[dayNum];
	    const hourEl = document.querySelector('[data-test-chart-name="Convos - busiest hour"] .superset-legacy-chart-big-number div')
	    const hour = parseInt(hourEl?.textContent);
	    if (hourEl && hour) hourEl.textContent = hour+':00'
	}, 1000);

})();