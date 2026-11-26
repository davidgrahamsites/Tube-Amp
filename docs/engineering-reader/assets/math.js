// Local KaTeX; document text remains readable if math rendering fails.
window.addEventListener('DOMContentLoaded', () => {
  window.readerMathErrors = [];
  renderMathInElement(document.querySelector('main') || document.body, {
    delimiters: [
      {left: '\\[', right: '\\]', display: true},
      {left: '\\(', right: '\\)', display: false}
    ],
    throwOnError: true,
    strict: false,
    trust: false,
    errorCallback: message => window.readerMathErrors.push(message)
  });
  document.documentElement.dataset.mathReady = 'true';
});
