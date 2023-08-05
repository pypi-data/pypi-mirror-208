window.addEventListener('load', function () {

  const selector = "input[data-password-visibility]";
  document.querySelector(selector).onclick = toggleE2EEPasswordVisibility;

  generateMnemonicPhrase().then(
    (passPhrase) => {
      const selector = "input[name=password][autocomplete=new-password]"
      document.querySelector(selector).value = passPhrase;
    }
  )
})

function toggleE2EEPasswordVisibility() {
  const selector = "input[name=password][autocomplete=new-password]";
  if (this.checked) {
    document.querySelector(selector).type = 'text';
  }
  else {
    document.querySelector(selector).type='password';
  }
}
