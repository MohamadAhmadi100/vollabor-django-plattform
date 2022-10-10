
$(document).ready(function(){
const individualBtn = document.getElementById('individual-button'),
corporationBtn = document.getElementById('corporation-button'),
userForms = document.getElementById('user_options-forms')

/**
 * Add event listener to the "Sign Up" button
 */
individualBtn.addEventListener('click', () => {
  userForms.classList.remove('animateLeft')
  userForms.classList.add('animateRight')
  document.getElementById("user_forms-individual").style.visibility = "visible"
  document.getElementById("user_forms-corporation").style.visibility = "hidden"
  
}, false)

/**
 * Add event listener to the "Login" button
 */
corporationBtn.addEventListener('click', () => {
  userForms.classList.remove('animateRight')
  userForms.classList.add('animateLeft')
  document.getElementById("user_forms-individual").style.visibility = "hidden"
  document.getElementById("user_forms-corporation").style.visibility = "visible"
}, false)
    
});



