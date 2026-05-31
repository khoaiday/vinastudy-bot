const fs = require('fs');
const path = require('path');
const vm = require('vm');

function check() {
    const htmlPath = path.join(__dirname, '..', 'tower_defense.html');
    const content = fs.readFileSync(htmlPath, 'utf8');

    // Simple script tag regex extractor
    const scriptRegex = /<script>([\s\S]*?)<\/script>/gi;
    let match;
    let idx = 0;

    while ((match = scriptRegex.exec(content)) !== null) {
        const jsCode = match[1];
        
        // Find the line number in HTML where this script starts
        const htmlBefore = content.substring(0, match.index);
        const startLineNum = htmlBefore.split('\n').length;

        console.log(`Checking script block ${idx} (starts at HTML line ${startLineNum})...`);
        
        try {
            // Attempt to compile the script content using node's vm module
            new vm.Script(jsCode, { filename: `tower_defense.html_script_${idx}.js` });
            console.log(`✅ Script block ${idx} is syntactically correct!`);
        } catch (err) {
            console.log(`❌ Syntax Error found in script block ${idx}!`);
            console.log(err.stack || err);
            
            // Extract the line number in the script and calculate HTML line number
            if (err.stack) {
                const lineMatch = err.stack.match(/tower_defense\.html_script_\d+\.js:(\d+)/);
                if (lineMatch) {
                    const jsErrLine = parseInt(lineMatch[1]);
                    const htmlErrLine = startLineNum + jsErrLine - 1;
                    console.log(`\n👉 Exact HTML line of syntax error is approximately: ${htmlErrLine}\n`);
                    
                    // Show a few lines of code around the error
                    const htmlLines = content.split('\n');
                    const startShow = Math.max(0, htmlErrLine - 5);
                    const endShow = Math.min(htmlLines.length - 1, htmlErrLine + 5);
                    console.log("Code snippet around error:");
                    for (let l = startShow; l <= endShow; l++) {
                        const marker = (l === htmlErrLine - 1) ? "👉 " : "   ";
                        console.log(`${marker}${l + 1}: ${htmlLines[l]}`);
                    }
                }
            }
        }
        idx++;
    }
}

check();
