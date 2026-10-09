with open('start_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add CSS
css_insert = """
        #bg-anim {
            position: fixed;
            top: -10%; left: -10%;
            width: 120%; height: 120%;
            z-index: -1;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            animation: panZoom 40s infinite alternate ease-in-out;
            opacity: 0.5;
            filter: blur(2px) contrast(1.1);
        }
        @keyframes panZoom {
            0% { transform: scale(1) translate(0, 0) rotate(0deg); }
            100% { transform: scale(1.1) translate(-2%, -1%) rotate(1deg); }
        }
"""
content = content.replace('</style>', css_insert + '</style>')

# Add div
body_insert = """<body>
    <div id="bg-anim"></div>"""
content = content.replace('<body>', body_insert)

# Add JS
js_insert = """
        const bgs = ['bg_1.jpg', 'bg_2.jpg', 'bg_3.jpg'];
        const randomBg = bgs[Math.floor(Math.random() * bgs.length)];
        document.getElementById('bg-anim').style.backgroundImage = "url('" + randomBg + "')";
"""
content = content.replace('<script>', '<script>' + js_insert)

# Change body bg so it doesn't block
content = content.replace('background-color: #0D0D12;', 'background-color: transparent;')

with open('start_page.html', 'w', encoding='utf-8') as f:
    f.write(content)
