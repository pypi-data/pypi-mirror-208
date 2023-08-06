
(function() {

    function sendValue(value) {
      Streamlit.setComponentValue(value)
    }

    async function onRender(event) {
      const {height} = event.detail.args;
      const {title} = event.detail.args;
      var {value} = event.detail.args;
      const {icon} = event.detail.args;
      const {progress} = event.detail.args;
      const {animate} = event.detail.args;
      const {unit} = event.detail.args;
      const {animateDuration} = event.detail.args;
      const {showProgress}= event.detail.args;
      const {showIcon}=event.detail.args;
      const {iconTop}=event.detail.args;
      const {iconLeft}=event.detail.args;
      const {iconColor}=event.detail.args;
      const {iconOpacity}=event.detail.args;
      const {backgroundColor}=event.detail.args;
      const {borderSize}=event.detail.args;
      const {titleColor}=event.detail.args;
      const {valueColor}=event.detail.args;
      const {progressColor}=event.detail.args;
      const {textAlign}=event.detail.args;
      
      Streamlit.setFrameHeight(height);
      var card=await waitForBody('.card')
      document.querySelector(".card").style.borderWidth=borderSize;
      document.querySelector("body").style.display='';
      card.style.height=height+"px";
      const titled = document.querySelector(".title span");
      const vald = document.querySelector(".card-content span");
      const icond = document.querySelector(".info-icon i");
      const pgb = document.querySelector(".progressbar");
      const iconParent=document.querySelector(".info-icon");
      const body=document.querySelector(".card");
      const text=document.querySelector(".header-row");
      text.style.textAlign=textAlign;
      vald.style.textAlign=textAlign;
      body.style.backgroundColor=backgroundColor;
      titled.style.color=titleColor;
      vald.style.color=valueColor;
      pgb.style.backgroundColor=progressColor;
      titled.innerHTML=title;
      
      var tryNumber = Number(value)
      if(isNaN(tryNumber)){
        vald.innerText=value;
        if(animate==true)
          animateText(vald,animateDuration);
      }
      else{
        oldVal=parseFloat(vald.innerText);
        if (isNaN(oldVal))
          oldVal=0
        if(animate==true)
          animateValue(vald,oldVal,tryNumber,animateDuration,unit);
        else
          vald.innerText=value  + unit;
      }
      
      pgb.style.width=progress+"%";
      if(showProgress==false){
        pgb.style.display='none';
      }
      else{
        pgb.style.display='';
      }
      if(showIcon==false){
        iconParent.style.display='none';
      }
      else{
        setTimeout(()=>{
          function fix(){
            var icond = document.querySelector(".info-icon i");
            icond.className='fa';
            icon.split(' ').forEach(element => {
              icond.classList.add(element);
            });
            iconParent.style.display='';
            var rangeH=(body.clientHeight-icond.clientHeight-pgb.clientHeight)*(iconTop/100)
            iconParent.style.top=Math.max(rangeH,0)+'px';
            var rangeV=(body.clientWidth-icond.clientWidth)*(iconLeft/100)
            iconParent.style.left=Math.min(rangeV,body.clientWidth-icond.clientWidth)+'px';
            icond.style.color=iconColor;
            icond.style.opacity=iconOpacity/100;
          }
          fix()
          setInterval(()=>{fix()},2500)
          
      },600)
      }
    }

    async function waitForBody(selector, timeout = 10000) {
      const start = Date.now();
    
      while (Date.now() - start < timeout) {
        const el = document.querySelector(selector);
        if (el) {
          return el;
        }
        console.log('Not found yet...')
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    
      return null;
    }

    function animateText(elem,duration){
      lengthVal=elem.innerText.length;
      delay=(duration/lengthVal) - (duration/lengthVal)/6
      elem.innerHTML = elem.textContent.replace(/\S/g, '<div style="display: inline-block;" class="letter">$&</div>');
      anime.timeline({loop: false})
      .add({
        targets: '.letter',
        rotateY: [-90, 0],
        duration: duration,
        delay: (el, i) => delay * i
      })
    }

    function animateValue(elem, start, end, duration,unit) {
      duration=duration-600;
      var realEnd=Intl.NumberFormat().format(end);
      var decimal = (realEnd+"").split(".")[1];
      end=parseInt(end)
      var obj = elem;
      var range = end - start;
      var minTimer = 5;
      var stepTime = Math.abs(Math.floor(duration / range));
      stepTime = Math.max(stepTime, minTimer);
      var startTime = new Date().getTime();
      var endTime = startTime + duration;
      var timer;
      function run() {
          var now = new Date().getTime();
          var remaining = Math.max((endTime - now) / duration, 0);
          var value = Math.floor(end - (remaining * range));
          var valFormat=Intl.NumberFormat().format(value)
          var render=valFormat +unit
          if(decimal)
            render=valFormat+'.'+ padZero(getRandomInt(decimal),decimal.toString().length) +unit
          obj.innerHTML = render;
          if (value == end) {
              clearInterval(timer);
              obj.innerHTML = realEnd+unit;
          }
      }
      
      timer = setInterval(run, stepTime);
      run();
    }

    function getRandomInt(max) {
      return Math.floor(Math.random() * max);
    }

    function padZero(num, places){
      return String(num).padStart(places, '0')
    }

    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
    Streamlit.setComponentReady();
})();

