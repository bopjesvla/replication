let p = require('puppeteer')
let fs = require('fs')
let fetch = require('node-fetch')

let data = JSON.parse(fs.readFileSync('titles-labels.json'))
let flat = [].concat.apply([], data.map(d => d.rows.map(r=>({authors: r[0].trim(), title: r[1].trim(), result: r[9].trim()}))))
    .filter(r => /\d/.test(r.result))
console.log(flat)

;(async _ => {
    const browser = await p.launch({})
    const page = await browser.newPage()
    page.on('console', console.log)
    process.on("unhandledRejection", e => {
        // console.log(await page.$eval('html', x => x ? x.innerText : ''))
        throw e
    })
    console.log('a')
    let headers = {
        'Content-Type': 'application/json'
    }
    let res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(0,50).map(t => t.authors + ' ' + t.title)), headers})
    let dois = (await res.json()).results.map(r => r.doi)
    console.log('success')
    res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(50, 100).map(t => t.authors + ' ' + t.title)), headers})
    dois = dois.concat((await res.json()).results.map(r => r.doi))
    res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(100, 150).map(t => t.authors + ' ' + t.title)), headers})
    dois = dois.concat((await res.json()).results.map(r => r.doi))
    res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(150).map(t => t.authors + ' ' + t.title)), headers})
    dois = dois.concat((await res.json()).results.map(r => r.doi))

    fs.writeFileSync('flat.json', JSON.stringify({data: flat, dois}))
    console.log(dois)
    return
    for (let t of flat) {
        await page.goto('https://sci-hub.tw')
        let input = await page.$('input[name=request]')
        let search = t.authors + ' ' + t.title

        console.log(search)
        await input.type(search)
        await page.waitFor(2000)
        await input.press('Enter')
        await page.waitForNavigation()
        await page.waitFor(2000)
        let pdf = await page.$eval('#pdf', pdf => pdf.src)
        console.log(pdf)
    }
})()
