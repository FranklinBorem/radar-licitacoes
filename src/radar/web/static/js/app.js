// JavaScript do site. Por enquanto, so preenche o ano no rodape.
document.addEventListener("DOMContentLoaded", () => {
  const ano = document.getElementById("ano");
  if (ano) ano.textContent = new Date().getFullYear();
});
