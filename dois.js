let p = require('puppeteer')
let fs = require('fs')
let fetch = require('node-fetch')

let data = JSON.parse(fs.readFileSync('titles-labels.json'))
let flat = [].concat.apply([], data.map(d => d.rows.map(r=>({
    authors: r[0].trim(), title: r[1].trim(), result: r[9].trim(), questioned: r[11].trim(),
    journal: r[2].trim(), year: r[3].trim(), edition: r[4].trim(), pages: r[5].trim(), jel: r[6].trim(),
    keywords: r[7].trim(), public: r[10].trim(), type: r[8].trim(), statement: r[12].trim(),
    replication: {
        authors: d.replication.rows[0][0].trim(),
        title: d.replication.rows[0][1].trim(),
        journal: d.replication.rows[0][2].trim(),
        year: d.replication.rows[0][3].trim(),
        edition: d.replication.rows[0][4].trim(),
        pages: d.replication.rows[0][5].trim(),
        jel: d.replication.rows[0][6].trim(),
        keywords: d.replication.rows[0][7].trim(),
    }
}))))
    .filter(r => r.title)
    // .filter(r => /\d/.test(r.result) || /\d/.test(r.questioned))

;(async _ => {
    process.on("unhandledRejection", e => {
        // console.log(await page.$eval('html', x => x ? x.innerText : ''))
        throw e
    })
    console.log('a')
    let headers = {
        'Content-Type': 'application/json'
    }
    for (let b = 0; b < flat.length; b += 50) {
        let batch = flat.slice(b, b+50)
        let res = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(batch.map(t => t.authors + ' ' + t.title)), headers})
        res = (await res.json()).results
        let repl = await fetch('https://search.crossref.org/links', {method: 'POST', body: JSON.stringify(batch.map(t => t.replication.authors + ' ' + t.replication.title)), headers})
        repl = (await repl.json()).results
        for (let i in batch) {
            batch[i].doi = res[i].doi
            batch[i].doiscore = res[i].score
            batch[i].replication.doi = repl[i].doi
            batch[i].replication.doiscore = repl[i].score
        }
    }

    fs.writeFileSync('flat.json', JSON.stringify(flat))
})()
