/* Progressive enhancement: answers remain visible without JavaScript. */
document.querySelectorAll('[data-prediction]').forEach(section => {
  const answer = section.querySelector('[data-answer]');
  const feedback = section.querySelector('[data-feedback]');
  const choices = [...section.querySelectorAll('[data-choice]')];
  if (!answer || !feedback || !choices.length) return;
  answer.hidden = true;
  choices.forEach(button => {
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => {
      choices.forEach(choice => choice.setAttribute('aria-pressed', String(choice === button)));
      answer.hidden = false;
      feedback.textContent = button.dataset.choice === 'correct'
        ? 'Exactly. Here is why.' : 'A reasonable guess. Here is the catch.';
    });
  });
});
