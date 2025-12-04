console.log("SpamShield content script loaded!");

const API_URL = "http://localhost:8000/predict";

// Insert "Check Spam" button
function insertCheckSpamButton() {
    const subjectElem = document.querySelector("h2.hP");

    if (!subjectElem) return;
    if (document.getElementById("checkSpamButton")) return;

    const btn = document.createElement("button");
    btn.id = "checkSpamButton";
    btn.textContent = "Check Spam";

    btn.style.cssText = `
        margin-left: 12px;
        padding: 8px 14px;
        background: #6e8efb;
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        font-size: 13px;
        transition: 0.2s;
    `;

    btn.onmouseover = () => btn.style.opacity = "0.85";
    btn.onmouseout = () => btn.style.opacity = "1";

    subjectElem.insertAdjacentElement("afterend", btn);

    btn.addEventListener("click", checkSpam);
}

// Handle spam scanning
async function checkSpam() {
    const subject = document.querySelector("h2.hP")?.innerText || "";
    const bodyElem = document.querySelector(".a3s.aiL");
    const body = bodyElem ? bodyElem.innerText : "";

    if (!body) {
        alert("Could not read email body.");
        return;
    }

    const payload = { text: `${subject}\n\n${body}` };

    let resultDiv = document.getElementById("spamResultBanner");
    if (!resultDiv) {
        resultDiv = document.createElement("div");
        resultDiv.id = "spamResultBanner";
        const subjectElem = document.querySelector("h2.hP");
        subjectElem.insertAdjacentElement("afterend", resultDiv);
    }

    addStyles();

    resultDiv.innerHTML = `
        <div class="spamCard">
            <div class="spinner"></div>
            <h3>Analyzing email...</h3>
            <p>Please wait while SpamShield checks this message.</p>
        </div>
    `;

    document.getElementById("checkSpamButton").style.display = "none";

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        const isSpam = data.prediction === "spam";
        const confidence = data.confidence;
        const spamProb = confidence ? (confidence[1] * 100).toFixed(2) : null;

        // UI CARDS WITH CONFIDENCE INCLUDED
        if (isSpam) {
            resultDiv.innerHTML = `
                <div class="spamCard spam">
                    <img src="https://cdn-icons-png.flaticon.com/512/463/463612.png" class="icon">
                    <h3>⚠️ Spam Detected!</h3>
                    <p>This email appears to be spam.</p>

                    ${spamProb ? `
                        <div class="confidenceBox">
                            <div class="bar spamBar" style="width: ${spamProb}%"></div>
                        </div>
                        <p class="confidenceText">Spam Probability: <b>${spamProb}%</b></p>
                    ` : ""}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="spamCard safe">
                    <img src="https://cdn-icons-png.flaticon.com/512/845/845646.png" class="icon">
                    <h3>✅ Safe Email</h3>
                    <p>No harmful patterns detected.</p>

                    ${spamProb ? `
                        <div class="confidenceBox">
                            <div class="bar safeBar" style="width: ${spamProb}%"></div>
                        </div>
                        <p class="confidenceText">Spam Probability: <b>${spamProb}%</b></p>
                    ` : ""}
                </div>
            `;
        }

    } catch (err) {
        console.error(err);
        resultDiv.innerHTML = `
            <div class="spamCard spam">
                <h3>⚠️ API Error</h3>
                <p>Unable to connect to prediction server.</p>
            </div>
        `;
    }
}

// Observer adds button whenever Gmail loads a new email
const observer = new MutationObserver(() => {
    insertCheckSpamButton();
});
observer.observe(document.body, { childList: true, subtree: true });

// UI Styles
function addStyles() {
    if (document.getElementById("spamStyles")) return;

    const style = document.createElement("style");
    style.id = "spamStyles";

    style.textContent = `
    .spamCard {
        width: 90%;
        margin-top: 15px;
        padding: 18px;
        border-radius: 14px;
        background: #ffffff;
        border-left: 6px solid #6e8efb;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        animation: fadeIn 0.4s ease;
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    .spamCard.spam {
        background: #ffe6e6;
        border-left-color: #ff3b3b;
    }

    .spamCard.safe {
        background: #e6ffe9;
        border-left-color: #00c851;
    }

    .spamCard h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 700;
    }

    .spamCard p {
        margin-top: 5px;
        opacity: 0.7;
        font-size: 13px;
    }

    .icon {
        width: 36px;
        margin-bottom: 8px;
    }

    .confidenceBox {
        width: 100%;
        height: 8px;
        background: #ddd;
        border-radius: 4px;
        margin: 10px 0 5px 0;
        overflow: hidden;
    }

    .bar {
        height: 100%;
        transition: width 0.4s ease;
    }

    .spamBar {
        background: #ff3b3b;
    }

    .safeBar {
        background: #00c851;
    }

    .confidenceText {
        font-size: 12px;
        opacity: 0.8;
    }

    .spinner {
        width: 32px;
        height: 32px;
        border: 4px solid #ddd;
        border-top-color: #6e8efb;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 10px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    `;

    document.head.appendChild(style);
}
