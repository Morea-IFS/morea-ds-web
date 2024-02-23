const dashboardNewsDiv = document.querySelector("#dashboard_news")
const iotNewsDiv = document.querySelector("#iot_news")

async function getNews(url, newsDiv) {
	let NewsHTML = ""

	//	Fetch Data
	const News = await fetch(`${url}`, {
		headers: {
			"X-GitHub-Api-Version": "2022-11-28",
		},
	}).then((res) => res.json())

	const emojis = await fetch("/static/js/emoji.json").then((res) => res.json())

	News.map((commit) => {
		const date = new Date(commit.commit.author.date)

		// Format Emojis for HTML
		let message = commit.commit.message
		let finalMessage

		const firstSeparator = message.indexOf(":")
		const secondSeparator = message.indexOf(":", 2)

		if (firstSeparator >= 0 && firstSeparator !== secondSeparator) {
			let subString = message.substring(firstSeparator, secondSeparator + 1)

			for (var i = 0; i < emojis.emojis.length; i++) {
				if (emojis.emojis[i]["shortname"] === subString) {
					finalMessage =
						emojis.emojis[i]["html"].split(";")[0] +
						" " +
						message.slice(secondSeparator + 2)
				}
			}
		}

		// Build HTML
		NewsHTML += `
		<div class="new_container">
			<div class="profile_container">
			  <img src="${commit.author.avatar_url}" alt="Profile Image">
			  <h3>${commit.commit.author.name}</h3>
			  <p>${date.format("d-m-Y")}</p>
			</div>
			<p>${finalMessage ? finalMessage : message}</p>
	  	</div>
	  `
	})

	newsDiv.innerHTML = NewsHTML
}

getNews("https://api.github.com/repos/Morea-IFS/morea-ds-web/commits", dashboardNewsDiv)
getNews("https://api.github.com/repos/Morea-IFS/morea-ds-iot/commits", iotNewsDiv)
