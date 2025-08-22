(() => {
	console.log('HLP SS custom JS loaded');
	const hlpDomains = ['https://hlpst.app', 'https://hlp.city', 'http://localhost:1906', 'https://stage.hlpst.app'];
	let hlpDomain;

	//listen for messages from HLP parent - must have an `id` property denoting message ID
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

})();