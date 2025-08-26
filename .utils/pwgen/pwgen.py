from flask import Flask, render_template_string, request, jsonify
import random
import string
import requests

app = Flask(__name__)

# Common word list for memorable passwords
COMMON_WORDS = [
    'apple', 'beach', 'chair', 'dream', 'eagle', 'flame', 'grace', 'house', 'image', 'juice',
    'knife', 'light', 'mouse', 'noise', 'ocean', 'peace', 'quiet', 'river', 'stone', 'table',
    'uncle', 'voice', 'water', 'youth', 'zebra', 'music', 'pizza', 'happy', 'smart', 'green',
    'quick', 'brown', 'black', 'white', 'round', 'small', 'large', 'sweet', 'fresh', 'clean',
    'cloud', 'plant', 'heart', 'world', 'power', 'money', 'space', 'truth', 'friend', 'magic'
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 16px;
            padding: 32px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .header {
            margin-bottom: 24px;
        }

        .header h1 {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 16px;
        }

        .tab-container {
            display: flex;
            gap: 4px;
            margin-bottom: 24px;
        }

        .tab {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            background: #f9fafb;
            text-align: center;
            cursor: pointer;
            font-weight: 500;
            color: #6b7280;
            transition: all 0.2s;
        }

        .tab.active {
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
        }

        .tab:hover:not(.active) {
            background: #f3f4f6;
            border-color: #d1d5db;
        }

        .section {
            margin-bottom: 24px;
        }

        .section h2 {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 16px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .slider-group {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .slider-group label {
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }

        .slider-container {
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
            margin: 0 16px;
        }

        .slider {
            flex: 1;
            height: 4px;
            border-radius: 2px;
            background: #e5e7eb;
            outline: none;
            appearance: none;
        }

        .slider::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
        }

        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
            border: none;
        }

        .value-display {
            background: #f3f4f6;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 600;
            color: #374151;
            min-width: 40px;
            text-align: center;
        }

        .toggle-group {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .toggle-group label {
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }

        .toggle {
            position: relative;
            width: 44px;
            height: 24px;
            border-radius: 12px;
            background: #e5e7eb;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .toggle.active {
            background: #3b82f6;
        }

        .toggle::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: white;
            top: 2px;
            left: 2px;
            transition: transform 0.2s;
        }

        .toggle.active::after {
            transform: translateX(20px);
        }

        .password-display {
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .password-text {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 18px;
            font-weight: 600;
            text-align: center;
            word-break: break-all;
        }

        .color-coded .uppercase { color: #dc2626; }
        .color-coded .lowercase { color: #2563eb; }
        .color-coded .number { color: #059669; }
        .color-coded .symbol { color: #7c3aed; }

        .button-group {
            display: flex;
            gap: 12px;
        }

        .btn {
            flex: 1;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
            border: 2px solid #3b82f6;
        }

        .btn-primary:hover {
            background: #2563eb;
            border-color: #2563eb;
        }

        .btn-secondary {
            background: white;
            color: #3b82f6;
            border: 2px solid #3b82f6;
        }

        .btn-secondary:hover {
            background: #f8fafc;
        }

        .hidden {
            display: none;
        }

        .checkbox-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .checkbox {
            width: 18px;
            height: 18px;
            border: 2px solid #d1d5db;
            border-radius: 4px;
            cursor: pointer;
            position: relative;
            background: white;
        }

        .checkbox.checked {
            background: #3b82f6;
            border-color: #3b82f6;
        }

        .checkbox.checked::after {
            content: '✓';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 12px;
            font-weight: bold;
        }

        .checkbox-item label {
            font-size: 14px;
            color: #6b7280;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Choose password type</h1>
            <div class="tab-container">
                <div class="tab active" data-type="random">⚡ Random</div>
                <div class="tab" data-type="memorable">💭 Memorable</div>
                <div class="tab" data-type="pin"># PIN</div>
            </div>
        </div>

        <!-- Random Password Options -->
        <div id="random-options" class="password-options">
            <div class="section">
                <h2>Customize your new password</h2>
                
                <div class="slider-group">
                    <label>Characters</label>
                    <div class="slider-container">
                        <input type="range" class="slider" id="random-length" min="4" max="50" value="16">
                    </div>
                    <div class="value-display" id="random-length-value">16</div>
                </div>

                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <div class="checkbox checked" data-option="lowercase"></div>
                        <label>Lowercase</label>
                    </div>
                    <div class="checkbox-item">
                        <div class="checkbox checked" data-option="uppercase"></div>
                        <label>Uppercase</label>
                    </div>
                    <div class="checkbox-item">
                        <div class="checkbox checked" data-option="numbers"></div>
                        <label>Numbers</label>
                    </div>
                    <div class="checkbox-item">
                        <div class="checkbox checked" data-option="symbols"></div>
                        <label>Symbols</label>
                    </div>
                </div>
            </div>
        </div>

        <!-- Memorable Password Options -->
        <div id="memorable-options" class="password-options hidden">
            <div class="section">
                <h2>Customize your new password</h2>
                
                <div class="slider-group">
                    <label>Characters</label>
                    <div class="slider-container">
                        <input type="range" class="slider" id="memorable-length" min="3" max="8" value="4">
                    </div>
                    <div class="value-display" id="memorable-length-value">4</div>
                </div>

                <div class="toggle-group">
                    <label>Capitalize the first letter</label>
                    <div class="toggle" data-option="capitalize"></div>
                </div>

                <div class="toggle-group">
                    <label>Use full words</label>
                    <div class="toggle active" data-option="full-words"></div>
                </div>
            </div>
        </div>

        <!-- PIN Options -->
        <div id="pin-options" class="password-options hidden">
            <div class="section">
                <h2>Customize your new password</h2>
                
                <div class="slider-group">
                    <label>Characters</label>
                    <div class="slider-container">
                        <input type="range" class="slider" id="pin-length" min="4" max="12" value="6">
                    </div>
                    <div class="value-display" id="pin-length-value">6</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Generated password</h2>
            <div class="password-display">
                <div class="password-text color-coded" id="password-output">4C-QD4T%ptGhMz@</div>
            </div>

            <div class="button-group">
                <button class="btn btn-primary" onclick="copyPassword()">Copy password</button>
                <button class="btn btn-secondary" onclick="generatePassword()">Refresh password</button>
            </div>
        </div>
    </div>

    <script>
        let currentType = 'random';
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                currentType = this.dataset.type;
                
                document.querySelectorAll('.password-options').forEach(option => {
                    option.classList.add('hidden');
                });
                
                document.getElementById(currentType + '-options').classList.remove('hidden');
                generatePassword();
            });
        });

        // Sliders
        document.querySelectorAll('.slider').forEach(slider => {
            const valueDisplay = document.getElementById(slider.id + '-value');
            
            slider.addEventListener('input', function() {
                valueDisplay.textContent = this.value;
                generatePassword();
            });
        });

        // Checkboxes
        document.querySelectorAll('.checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', function() {
                this.classList.toggle('checked');
                generatePassword();
            });
        });

        // Toggles
        document.querySelectorAll('.toggle').forEach(toggle => {
            toggle.addEventListener('click', function() {
                this.classList.toggle('active');
                generatePassword();
            });
        });

        function generateRandomPassword() {
            const length = parseInt(document.getElementById('random-length').value);
            const options = {
                lowercase: document.querySelector('[data-option="lowercase"]').classList.contains('checked'),
                uppercase: document.querySelector('[data-option="uppercase"]').classList.contains('checked'),
                numbers: document.querySelector('[data-option="numbers"]').classList.contains('checked'),
                symbols: document.querySelector('[data-option="symbols"]').classList.contains('checked')
            };

            let chars = '';
            if (options.lowercase) chars += 'abcdefghijklmnopqrstuvwxyz';
            if (options.uppercase) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            if (options.numbers) chars += '0123456789';
            if (options.symbols) chars += '!@#$%^&*()-_=+[]{}|;:,.<>?';

            if (!chars) return 'Select at least one option';

            let password = '';
            for (let i = 0; i < length; i++) {
                password += chars.charAt(Math.floor(Math.random() * chars.length));
            }

            return colorCodePassword(password);
        }

        function generateMemorablePassword() {
            const wordCount = parseInt(document.getElementById('memorable-length').value);
            const capitalize = document.querySelector('[data-option="capitalize"]').classList.contains('active');
            const fullWords = document.querySelector('[data-option="full-words"]').classList.contains('active');

            let words = [];
            
            for (let i = 0; i < wordCount; i++) {
                if (fullWords) {
                    const word = getRandomWord();
                    words.push(capitalize && i === 0 ? capitalizeFirst(word) : word);
                } else {
                    const length = Math.floor(Math.random() * 2) + 3; // 3-4 letters
                    let word = '';
                    const vowels = 'aeiou';
                    const consonants = 'bcdfghjklmnpqrstvwxyz';
                    
                    for (let j = 0; j < length; j++) {
                        if (j % 2 === 0) {
                            word += consonants[Math.floor(Math.random() * consonants.length)];
                        } else {
                            word += vowels[Math.floor(Math.random() * vowels.length)];
                        }
                    }
                    words.push(capitalize && i === 0 ? capitalizeFirst(word) : word);
                }
            }

            return words.join('-');
        }

        function generatePIN() {
            const length = parseInt(document.getElementById('pin-length').value);
            let pin = '';
            for (let i = 0; i < length; i++) {
                pin += Math.floor(Math.random() * 10).toString();
            }
            return pin;
        }

        function getRandomWord() {
            const words = [
                'apple', 'beach', 'chair', 'dream', 'eagle', 'flame', 'grace', 'house', 'image', 'juice',
                'knife', 'light', 'mouse', 'noise', 'ocean', 'peace', 'quiet', 'river', 'stone', 'table',
                'uncle', 'voice', 'water', 'youth', 'zebra', 'music', 'pizza', 'happy', 'smart', 'green',
                'quick', 'brown', 'black', 'white', 'round', 'small', 'large', 'sweet', 'fresh', 'clean',
                'cloud', 'plant', 'heart', 'world', 'power', 'money', 'space', 'truth', 'friend', 'magic',
                'woozy', 'episode', 'asano', 'slag', 'rational', 'chung'
            ];
            return words[Math.floor(Math.random() * words.length)];
        }

        function capitalizeFirst(word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
        }

        function colorCodePassword(password) {
            return password.split('').map(char => {
                if (char >= 'A' && char <= 'Z') {
                    return `<span class="uppercase">${char}</span>`;
                } else if (char >= 'a' && char <= 'z') {
                    return `<span class="lowercase">${char}</span>`;
                } else if (char >= '0' && char <= '9') {
                    return `<span class="number">${char}</span>`;
                } else {
                    return `<span class="symbol">${char}</span>`;
                }
            }).join('');
        }

        function generatePassword() {
            const output = document.getElementById('password-output');
            let password = '';

            switch (currentType) {
                case 'random':
                    password = generateRandomPassword();
                    break;
                case 'memorable':
                    password = generateMemorablePassword();
                    break;
                case 'pin':
                    password = generatePIN();
                    break;
            }

            output.innerHTML = password;
        }

        function copyPassword() {
            const passwordElement = document.getElementById('password-output');
            const password = passwordElement.textContent || passwordElement.innerText;
            
            navigator.clipboard.writeText(password).then(() => {
                const btn = document.querySelector('.btn-primary');
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.style.background = '#10b981';
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '#3b82f6';
                }, 1000);
            });
        }

        // Initial password generation
        generatePassword();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)