chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === "scan") {
        sendResponse({ received: true });
    }
});
