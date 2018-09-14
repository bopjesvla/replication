let p = require('puppeteer')
let fs = require('fs')
let fetch = require('node-fetch')

let data = JSON.parse(fs.readFileSync('titles-labels.json')).concat(JSON.parse(fs.readFileSync('titles-labels-multiple.json')))
let flat = [].concat.apply([], data.map(d => d.rows.map(r=>({
    authors: r[0].trim(), title: r[1].trim(), result: r[9].trim(), questioned: r[11].trim(),
    journal: r[2].trim(), year: r[3].trim(), edition: r[4].trim(), pages: r[5].trim(), jel: r[6].trim(),
    keywords: r[7].trim(), public: r[10].trim(), type: r[8].trim(), statement: r[12].trim(),
    replication: d.replication
}))))
    .filter(r => /\d/.test(r.result) || /\d/.test(r.questioned))
console.log(flat)

;(async _ => {
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
    res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(150, 200).map(t => t.authors + ' ' + t.title)), headers})
    dois = dois.concat((await res.json()).results.map(r => r.doi))
    res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(200, 250).map(t => t.authors + ' ' + t.title)), headers})
    dois = dois.concat((await res.json()).results.map(r => r.doi))
    res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(flat.slice(250).map(t => t.authors + ' ' + t.title)), headers})
    dois = dois.concat((await res.json()).results.map(r => r.doi))

    fs.writeFileSync('flat.json', JSON.stringify({data: flat, dois}))
    console.log(dois)
})()
