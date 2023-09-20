// window.addEventListener('load', () => {
//     console.log('load');
//     payload = {
//         topic: 'refresh',
//         message: ''
//     }
//     window.api.send('toMain',payload);
// })
const durationRestStability = 15;
$(function() {
    console.log('index.js')

    $("#pageContent").empty();
    $("#pageContent *").off(); 
    $("#pageContent").load("app/accueil/accueil.html");

    // $("#pageContent").load("app/test/test.html");



// let button = document.getElementById('test');
// button.addEventListener('click', () => {
//     window.api.send('toMain', {code: '1'})
// })


window.api.receive('fromMain', (payload) => {


    if (payload.topic == 'config') {
        console.log(data);
        durationRestStability = payload.data[0].durationRestStability;
    }
    //console.log(payload);
    // if (payload.topic == 'screen') {
    //     if (payload.message == 0) {
    //         $("#pageContent").load("app/accueil/accueil.html");
    //     }
    // }
    if (payload.topic == 'fromPython') {
        if (payload.status == 'start' && payload.essai == 0) {
            $("#pageContent").empty();
            $("#pageContent *").off(); 
            $("#pageContent").load("app/test/test.html");

        }
        if (payload.status == 'end') {
            $("#pageContent").empty();
            $("#pageContent *").off(); 
            $("#pageContent").load("app/resultat/resultat.html");
        }
        if (payload.status == 'newSession') {
            window.location.reload();
            $("#pageContent").empty();
            $("#pageContent *").off(); 
            $("#pageContent").load("app/accueil/accueil.html");


        }

    }



})

})