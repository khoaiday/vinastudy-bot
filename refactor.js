const fs = require('fs');

let html = fs.readFileSync('daiviet_defense/index.html', 'utf8');

const towerDrawNew = `
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                let imgKey = this.type + '_tower';
                if (assets[imgKey] && assets[imgKey].complete) {
                    const rec = this.recoil;
                    ctx.rotate(this.angle); // Rotate towards target
                    ctx.drawImage(assets[imgKey], -CELL_SIZE/2, -CELL_SIZE/2, CELL_SIZE, CELL_SIZE);
                    
                    if (rec > 0) {
                        ctx.fillStyle = 'rgba(255, 200, 0, 0.5)';
                        ctx.beginPath();
                        ctx.arc(CELL_SIZE/2, 0, rec, 0, Math.PI*2);
                        ctx.fill();
                    }
                }

                ctx.restore();

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.fillStyle = '#C8960C';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                let stars = '★';
                if (this.level === 2) stars = '★★';
                else if (this.level === 3) stars = '★★★';
                ctx.fillText(stars, 0, CELL_SIZE / 2 - 2);
                ctx.restore();
            }
`;
html = html.replace(/draw\(\) \{[\s\S]*?\/\/ 4\. Draw Gold star rating level indicators at the bottom edge[\s\S]*?ctx\.restore\(\);\n\s*\}/, towerDrawNew.trim());

const enemyDrawNew = `
            draw() {
                if (this.isDead) return;

                ctx.save();
                ctx.translate(this.x, this.y);

                const wobbleAngle = Math.sin(this.wobbleTime) * 0.08;
                const wobbleScaleY = 1 + Math.cos(this.wobbleTime) * 0.05;
                ctx.rotate(wobbleAngle);
                ctx.scale(1, wobbleScaleY);

                if (this.slowTimer > 0) {
                    ctx.beginPath();
                    ctx.arc(0, 0, this.radius + 4, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(90, 188, 170, 0.8)';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                let imgKey = 'enemy_soldier';
                if (this.name.includes('Trinh Sát')) imgKey = 'enemy_scout';
                else if (this.name.includes('Voi Chiến')) imgKey = 'enemy_heavy';
                else if (this.isAir) imgKey = 'enemy_air';
                else if (this.name.includes('Đại Tướng')) imgKey = 'enemy_heavy'; 

                if (assets[imgKey] && assets[imgKey].complete) {
                    const drawSize = this.radius * 2.5;
                    ctx.drawImage(assets[imgKey], -drawSize/2, -drawSize/2, drawSize, drawSize);
                }

                ctx.restore();

                ctx.save();
                ctx.translate(this.x, this.y);
                const barW = this.radius * 2;
                const barH = 4;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
                ctx.fillRect(-barW / 2, -this.radius - 8, barW, barH);
                const hpPct = Math.max(0, this.hp / this.maxHp);
                ctx.fillStyle = hpPct > 0.5 ? '#5ABCAA' : hpPct > 0.2 ? '#C8960C' : '#C0332E';
                ctx.fillRect(-barW / 2, -this.radius - 8, barW * hpPct, barH);
                ctx.restore();
            }
`;
html = html.replace(/draw\(\) \{\n\s*if \(this\.isDead\) return;\n\s*\/\/ --- DRAW AIR UNIT ---[\s\S]*?ctx\.fillRect\(-barW \/ 2, -this\.radius - 8, barW \* hpPct, barH\);\n\s*ctx\.restore\(\);\n\s*\}/, enemyDrawNew.trim());

const mapTileNew = `
            // 1. Draw map background
            if (assets.map_tile && assets.map_tile.complete) {
                for (let c = 0; c < COLS; c++) {
                    for (let r = 0; r < ROWS; r++) {
                        ctx.drawImage(assets.map_tile, c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                    }
                }
            } else {
                ctx.fillStyle = '#0f0714';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }
`;
html = html.replace(/\/\/ 1\. Draw antique background grid[\s\S]*?ctx\.fillRect\(0, 0, canvas\.width, canvas\.height\);/, mapTileNew.trim());

const initNew = `
        // Initialize board AFTER assets load
        document.querySelector('.start-btn').innerText = 'Đang tải ảnh... (0%)';
        initAssets(() => {
            document.querySelector('.start-btn').innerText = 'XUẤT QUÂN TRẬN ĐỒ';
            initLevelLayout(); // Khởi tạo ban đầu với Level 1
            drawBoard();
            updateUI();
        });
`;
html = html.replace(/initLevelLayout\(\); \/\/ Khởi tạo ban đầu với Level 1\n\s*drawBoard\(\);\n\s*updateUI\(\);/, initNew.trim());

fs.writeFileSync('daiviet_defense/index.html', html);
console.log('Replaced successfully');
