console.log("📩 Gmail Spam Checker content script running...");

const API_URL = "http://localhost:8000/predict";

// ========= FUNCTIONS ==========

// Reusable preprocessing function
function insertCheckSpamButton() {
  const subjectElem = document.querySelector("h2.hP"); // Gmail subject
  const existingButton = document.getElementById("checkSpamButton");

  // If email is open and button not already present
  if (subjectElem && !existingButton) {
    const btn = document.createElement("button");
    btn.id = "checkSpamButton";
    btn.textContent = "Check Spam";
    btn.style.marginLeft = "10px";
    btn.style.padding = "6px 12px";
    btn.style.border = "none";
    btn.style.borderRadius = "4px";
    btn.style.background = "#4caf50";
    btn.style.color = "white";
    btn.style.cursor = "pointer";
    btn.style.fontWeight = "bold";

    subjectElem.insertAdjacentElement("afterend", btn);
    btn.addEventListener("click", checkSpam);

    console.log("✅ Added Check Spam button");
  }
}

// Called when button is clicked
async function checkSpam() {
  const subject = document.querySelector("h2.hP")?.innerText || "";
  const bodyElem = document.querySelector(".a3s.aiL");
  const body = bodyElem ? bodyElem.innerText : "";

  if (!body) {
    alert("Could not read email content. Try opening the email fully.");
    return;
  }

  // Hide the button while checking
  const btn = document.getElementById("checkSpamButton");
  if (btn) {
    btn.disabled = true;
    btn.style.opacity = "0.5";
    btn.textContent = "Checking...";
    btn.style.cursor = "not-allowed";
  }

  const payload = { text: `${subject}\n\n${body}` };

  // Create or reuse result div
  const resultDivId = "spamResultBanner";
  let resultDiv = document.getElementById(resultDivId);
  if (!resultDiv) {
    resultDiv = document.createElement("div");
    resultDiv.id = resultDivId;
    resultDiv.style.marginTop = "10px";
    resultDiv.style.padding = "10px";
    resultDiv.style.borderRadius = "5px";
    resultDiv.style.fontWeight = "bold";
    const subjectElem = document.querySelector("h2.hP");
    subjectElem.insertAdjacentElement("afterend", resultDiv);
  }

  resultDiv.textContent = "Checking...";
  resultDiv.style.background = "gray";
  resultDiv.style.color = "white";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    const isSpam = data.prediction === "spam";

    resultDiv.textContent = isSpam ? "🚨 Spam Detected!" : "✅ Not Spam";
    resultDiv.style.background = isSpam ? "red" : "green";
    resultDiv.style.color = "white";

    // Permanently hide the button after result shown
    if (btn) {
      btn.style.display = "none";
    }
  } catch (error) {
    console.error("Error contacting API:", error);
    resultDiv.textContent = "⚠️ API Error. Check console.";
    resultDiv.style.background = "orange";

    // Re-enable the button if API failed
    if (btn) {
      btn.disabled = false;
      btn.style.opacity = "1";
      btn.textContent = "Check Spam";
      btn.style.cursor = "pointer";
    }
  }
}

// ========= OBSERVER LOGIC ==========

// This observer keeps checking if Gmail's DOM changed (e.g., new email opened)
const observer = new MutationObserver(() => {
  const subjectElem = document.querySelector("h2.hP");
  const existingButton = document.getElementById("checkSpamButton");

  // Only add button if an email is open and button not present
  if (subjectElem && !existingButton) {
    insertCheckSpamButton();
  }
});

// Start observing the entire Gmail body
observer.observe(document.body, { childList: true, subtree: true });

console.log("👀 Watching Gmail DOM for new emails...");
