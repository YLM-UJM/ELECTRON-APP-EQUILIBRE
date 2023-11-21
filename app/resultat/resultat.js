$(function() {

    const nouvelleSession = document.getElementById('nouvelleSession');
    const nouvelleEssai = document.getElementById('nouvelleEssai');


    window.api.receive('fromMain', (payload) => {
        if (payload.topic == 'fromPython') {
            if (payload.status == 'result') {
                const scoreR = payload.scoreR.value;
                const scoreL = payload.scoreL.value;
                const healthScoreR = payload.scoreR.healthScore;
                const healthScoreL = payload.scoreL.healthScore;
    
                // Mettre à jour les valeurs des scores dans les éléments HTML
                document.getElementById('scoreLValue').innerHTML = scoreL + ' mm<sup>2</sup>' + ' => ' + healthScoreL + '%' ;
                document.getElementById('scoreRValue').innerHTML = scoreR + ' mm<sup>2</sup>' + ' => ' + healthScoreR + '%' ;;
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