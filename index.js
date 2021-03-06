var p = require('puppeteer')
var fs = require('fs')

;(async _ => {
    const browser = await p.launch()
    const page = await browser.newPage()
    page.on('console', console.log)
    process.on("unhandledRejection", e => {
        // console.log(await page.$eval('html', x => x ? x.innerText : ''))
        throw e
    })

    let data = []

    // let url = 'http://replication.uni-goettingen.de/wiki/index.php/Category:Replication'
    let urls = ['http://replication.uni-goettingen.de/wiki/index.php/Category:Replication',
                'http://replication.uni-goettingen.de/wiki/index.php/Category:Replication_of_more_than_one_study']

    for (let url of urls) {
        while (url) {
            await page.goto(url)

            url = await page.$$eval('a', as => {
                let next = [...as].find(a => a.innerHTML == 'next 200')
                console.log(next)
                return next && next.href
            })

            let repls = await page.$$eval('#mw-pages > .mw-content-ltr ul > li > a', links => {
                return [...links].map(a => ({href: a.href, title: a.title}))
            })

            for (let r of repls) {
                console.log(r)
                await page.goto(r.href)

                let replication =  await page.$eval('#Article', articleHeader => {
                    let table = articleHeader.parentNode.nextElementSibling
                    let headers = [...table.querySelectorAll('th')].map(t => t.innerText)
                    let rows = [...table.querySelectorAll('tbody tr:not(:first-child)')].map(r => {
                        let results = [...r.children].map(t => t.innerText)
                        let paperLink = r.children[1].querySelector('a')
                        results.push(paperLink && paperLink.title)
                        return results
                    })
                    return {headers, rows}
                })
                console.log(replication)

                let {headers, rows} = await page.$eval('[title^="1=successful"]', resultHeaderLink => {
                    let table = resultHeaderLink.closest('table')
                    let headers = [...table.querySelectorAll('th')].map(t => t.innerText)
                    let rows = [...table.querySelectorAll('tbody tr')].map(r => {
                        let results = [...r.children].map(t => t.innerText)
                        let paperLink = r.children[1].querySelector('a')
                        results.push(paperLink && paperLink.title)
                        return results
                    })
                    return {headers, rows}
                })
                console.log(rows[0].slice(-1)[0])
                data.push({headers, rows, replication})
            }
        }
    }

    fs.writeFileSync('titles-labels.json', JSON.stringify(data))

    await browser.close()
})()
