// ===== गोपाल चायवाला — साइट सेटिंग्स =====
// यहां अपना असली WhatsApp नंबर डालें (देश कोड के साथ, बिना + या स्पेस के — जैसे 919812345678)
const WHATSAPP_NUMBER = "91XXXXXXXXXX";

document.getElementById("year").textContent = new Date().getFullYear();

// पैकेज कार्ड पर क्लिक करने पर, बुकिंग फॉर्म में वही पैकेज पहले से चुना हुआ आ जाए
document.querySelectorAll("[data-package]").forEach((el) => {
  el.addEventListener("click", () => {
    const pkg = el.getAttribute("data-package");
    const select = document.getElementById("package");
    if (select) {
      [...select.options].forEach((opt) => {
        if (opt.value === pkg) select.value = pkg;
      });
    }
  });
});

// फॉर्म सबमिट होने पर — सीधे WhatsApp पर पहले से भरा हुआ मैसेज खोल दो
const form = document.getElementById("bookingForm");
form.addEventListener("submit", (e) => {
  e.preventDefault();

  const data = Object.fromEntries(new FormData(form).entries());

  const lines = [
    "नमस्ते गोपाल चायवाला 🙏",
    "मुझे इवेंट के लिए बुकिंग करनी है:",
    "",
    `नाम: ${data.name}`,
    `फोन: ${data.phone}`,
    `इवेंट की तारीख: ${data.eventDate}`,
    data.eventType ? `इवेंट टाइप: ${data.eventType}` : "",
    `पैकेज: ${data.package}`,
    data.message ? `डिटेल: ${data.message}` : "",
  ].filter(Boolean).join("\n");

  const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(lines)}`;
  window.open(url, "_blank");
});

// फुटर वाला WhatsApp लिंक भी सेट कर दो
const waLink = document.getElementById("waLink");
if (waLink) waLink.href = `https://wa.me/${WHATSAPP_NUMBER}`;