var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var content = document.getElementsByClassName("content");
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

function readUrl(input) {
document.getElementById('bgPicError').innerHTML = '';
  if (input.files && input.files[0]) {
    let reader = new FileReader();
    reader.onload = (e) => {
      let imgData = e.target.result;
      let imgName = input.files[0].name;
      input.setAttribute("data-title", imgName);
      console.log(e.target.result);
    }
    reader.readAsDataURL(input.files[0]);
  }
  
  
  Filevalidation();
  
  
}


function Filevalidation(){
        const fi = document.getElementById('inputFile');
       
        if (fi.files.length > 0) {
            const fsize = fi.files.item(0).size;
            const file = Math.round((fsize / 1024));
           	if (file >= 5120) {
             	document.getElementById('bgPicError').innerHTML = 'File size must be less than 5 Mb';
             	if(focus_status == false){
    			document.getElementById("bgPicError").focus();	
    			focus_status = true;
	        	}
           }else{
               
               document.getElementById('bgPicError').innerHTML ='';
               
           } 
          
		  
        }
   }


