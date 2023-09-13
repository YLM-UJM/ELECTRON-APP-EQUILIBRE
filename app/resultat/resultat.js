$(function() {

    const nouvelleSession = document.getElementById('nouvelleSession');
    const nouvelleEssai = document.getElementById('nouvelleEssai');


    window.api.receive('fromMain', (payload) => {
        if (payload.topic == 'fromPython') {
            if (payload.status == 'result') {
                const scoreR = payload.scoreR.value;
                const scoreL = payload.scoreL.value;
    
                // Mettre à jour les valeurs des scores dans les éléments HTML
                document.getElementById('scoreLValue').innerHTML = scoreL + ' mm<sup>2</sup>';
                document.getElementById('scoreRValue').innerHTML = scoreR + ' mm<sup>2</sup>';
            }
        }
    })

    nouvelleSession.addEventListener('click', () => {
        payload = {
            'topic': 'toPython',
            'status': 'newSession',
            'essai': 10000
        }
        window.api.send('toMain', payload);
      })
    


})