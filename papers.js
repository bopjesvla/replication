let fs = require('fs')
let fetch = require('node-fetch')

let data = JSON.parse(fs.readFileSync('flat.json'))

process.on("unhandledRejection", e => {
    // console.log(await page.$eval('html', x => x ? x.innerText : ''))
    throw e
})

;(async _ => {
    for (let i in data.data) {
        let fn = 'papers/' + data.data[i].title + '.pdf'
        let match
        if (fs.existsSync(fn)) continue
        try {
            let res = await fetch('https://sci-hub.tw/' + data.dois[i])
            let html = await res.text()
            match = html.match(/iframe.*src\s*=\s*"([^"]+)"/)
            console.log(match)
            if (match) {
                let url = match[1].startsWith('//') ? 'https:' + match[1] : match[1]
                let res = await fetch(url)
                res.body.pipe(fs.createWriteStream(fn))
            }
        }
        catch (e) {
            console.log(e)
        }
        await new Promise(r => setTimeout(r, 10000))
    }
})()
