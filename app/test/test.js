// const { writeSync } = require("node:original-fs");

$(function() {


    function showDiv(className) {
        $('.ready, .test, .no-detected, .end, .step1Done, .ready2, .recup').removeClass('active');
        $(`.${className}`).addClass('active');
      }


      var countDownTest = document.getElementById('countDownTest');
      var countDownRecup = document.getElementById('countDownRecup');
      var side = document.getElementById('side');
      var cercle = document.getElementById('cercle');
      var essai = 1;
      console.log('essai : ', essai);
    //   side.textContent = 'droit.'
      console.log(essai);
    //   showDiv('');

      window.api.receive('fromMain', (payload) => {
        // console.log(payload)
        if (payload.topic == 'fromPython') {
            if (payload.status == 'no-detect') {
                console.log(essai);
                showDiv('no-detected');
                if (essai == 2) {
                    side.textContent = 'droit.'
                }
            }
            if (payload.status == 'on-running') {
                console.log(essai)
                if (payload.decompte == 0) {
                    if (essai == 1) {
                        essai = 2
                        recup(countDownRecup, essai);
                    } else  {
                        // fin du test 
                        console.log('fin du test')
                        payload = {
                            'topic': 'toPython',
                            'status': 'end',
                            'essai': 1000
                        }   
                        window.api.send('toMain', payload);
                    }
                } else {
                    countDownTest.textContent = payload.decompte;
                }

            }
            if (payload.status == 'detect ok') {
                showDiv('test');
                countDownTest.textContent = payload.decompte;
            }
            if (payload.status == 'start') {
                if (essai == 1) {
                    showDiv('ready')
                } 
            }
            if (payload.status == 'result') {
                // if (essai == 1) {
                //     essai = 2;
                //     recup(countDownRecup, essai);

                // }
                

            }
        }

})


let restart = document.getElementById('restart');
restart.addEventListener('click', () => {
  payload = {
      'topic': 'toPython',
      'status': 'start',
      'essai': essai,
      'autre': 'restart'
  }
window.api.send('toMain', payload);
if (essai == 1) {
    showDiv('ready');
} 
if (essai == 2) {
    showDiv('ready2');
}

})

function recup(countDownRecup, essai) {
    let rest = 1;
    showDiv('recup');
    countDownRecup.textContent = rest;
    const timerInterval = setInterval(() => {
        rest -= 1;
        countDownRecup.textContent = rest;
        if (rest == 0) {
            clearInterval(timerInterval);
            payload = {
                'topic': 'toPython',
                'status': 'start',
                'essai': essai,
                'type': 'recup'
            }
            window.api.send('toMain', payload);
            console.log('fin recup');
            showDiv('ready2')
        }
    },1000);
}

})