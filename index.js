window.onload = function() {


let button = document.getElementById('test');
button.addEventListener('click', () => {
    window.api.send('toMain', {topic: 'test', message: 'test'})
})

}