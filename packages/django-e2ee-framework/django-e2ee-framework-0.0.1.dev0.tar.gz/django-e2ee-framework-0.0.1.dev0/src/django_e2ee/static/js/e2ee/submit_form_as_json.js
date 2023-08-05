function submitFormAsJSON(event) {
  if (typeof(event.srcElement.form) === "undefined") {
    event.preventDefault();
  }

  function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

  let form = event.srcElement.form ? event.srcElement.form : event.srcElement;
  let formData = new FormData(form);

  let arrayData = Array.from(formData.entries(), ([x, y]) => ({ [x]: y }));

  let data = arrayData.length ? Object.assign(...arrayData) : {};

  return fetch(
    form.action,
    {
      "method": data.method ? data.method : form.method,
      body: JSON.stringify(data),
      headers: {
        'X-CSRFTOKEN': getCookie("csrftoken"),
        'Content-Type': 'application/json'
      }
    }
  )
}

function submitFormAndReload(event) {
  return submitFormAsJSON(event).then(response => {
    if ((response.status >= 200) && (response.status < 300)) {
      window.location = window.location;
    } else {
      console.error("Request failed", response);
      alert("Request failed! Please check the console for more information.");
    }
  })
}

window.addEventListener('load', function () {
  document.querySelectorAll("input[type=submit][name=submit_json_]").forEach(
    elem => {
      elem.form.onsubmit = submitFormAndReload;
    }
  )
})
