const form = document.querySelector("#chatForm");
const messages = document.querySelector("#messages");
const messageInput = document.querySelector("#messageInput");
const imageInput = document.querySelector("#imageInput");
const fileLabel = document.querySelector("#fileLabel");
let currentMode = "unified";

document.querySelectorAll(".chips button").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt;
    messageInput.focus();
  });
});

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  fileLabel.textContent = file ? file.name : "사진 첨부 가능";
});

function scrollBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function addUserMessage(text, file) {
  if (file) {
    const url = URL.createObjectURL(file);
    messages.insertAdjacentHTML("beforeend", `
      <article class="message user-msg image-preview">
        <img src="${url}" alt="업로드 이미지" />
        <p>피부 사진 1장</p>
      </article>
    `);
  }
  if (text) {
    messages.insertAdjacentHTML("beforeend", `<article class="message user-msg">${escapeHtml(text)}</article>`);
  }
  scrollBottom();
}

function addLoading() {
  const id = `loading-${Date.now()}`;
  messages.insertAdjacentHTML("beforeend", `
    <article id="${id}" class="message bot-card">
      <div class="bot-title"><span class="bot-icon">AI</span><strong>분석 중</strong></div>
      <p>이미지와 질문을 바탕으로 상담 답변을 준비하고 있습니다.</p>
    </article>
  `);
  scrollBottom();
  return id;
}

function renderDiagnosis(diagnosis) {
  if (!diagnosis) return "";
  const top = diagnosis.top_predictions || [];
  const first = top[0] ? `${escapeHtml(top[0].label)}(신뢰도: ${(top[0].confidence * 100).toFixed(1)}%)` : "";
  const second = top[1] ? `, ${escapeHtml(top[1].label)}(${(top[1].confidence * 100).toFixed(1)}%)` : "";
  return `
    <div class="diagnosis">
      <div><strong>진단보조 결과:</strong><span>${first}${second}</span></div>
    </div>
    <div class="notice">${escapeHtml(diagnosis.notice)}</div>
  `;
}

function addBotMessage(data, loadingId) {
  const title = data.route === "makeup" ? "AI 메이크업 가이드" : "AI 피부상담";
  const actions = (data.suggestions || []).map((item) => `<button type="button" data-prompt="${escapeHtml(item)}">${escapeHtml(item)}</button>`).join("");
  const html = `
    <div class="bot-title"><span class="bot-icon">AI</span><strong>${title}</strong></div>
    ${renderDiagnosis(data.diagnosis)}
    <p>${escapeHtml(data.answer || "").replaceAll("\n", "<br>")}</p>
    <div class="notice">AI 분석은 참고용이며 정확한 진단은 의료진 상담이 필요합니다.</div>
    <div class="bot-actions">${actions}</div>
  `;
  const loading = document.getElementById(loadingId);
  if (loading) loading.innerHTML = html;
  loading?.querySelectorAll(".bot-actions button").forEach((button) => {
    button.addEventListener("click", () => {
      messageInput.value = button.dataset.prompt;
      messageInput.focus();
    });
  });
  scrollBottom();
}

function addErrorMessage(text, loadingId) {
  const loading = document.getElementById(loadingId);
  const html = `
    <div class="bot-title"><span class="bot-icon">AI</span><strong>오류</strong></div>
    <p>${escapeHtml(text)}</p>
  `;
  if (loading) loading.innerHTML = html;
  scrollBottom();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  const file = imageInput.files[0];
  if (!text && !file) return;

  addUserMessage(text, file);
  const loadingId = addLoading();

  const formData = new FormData();
  formData.append("message", text);
  formData.append("mode", currentMode);
  if (file) formData.append("image", file);

  messageInput.value = "";
  imageInput.value = "";
  fileLabel.textContent = "사진 첨부 가능";

  try {
    const response = await fetch("/api/chat", { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.answer || data.error || "처리 실패");
    addBotMessage(data, loadingId);
  } catch (error) {
    addErrorMessage(error.message, loadingId);
  }
});

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
