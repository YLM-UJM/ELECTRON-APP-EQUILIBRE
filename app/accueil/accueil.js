$(function() {
    let userTest = false;
    i = 0;
    const startCountdown = document.getElementById('startCountdown');
    startCountdown.disabled = true;

    $('.carousel').carousel();

        // Ajout de gestionnaires d'événements pour les boutons du carousel
        $('.carousel-control-prev').on('click', function() {
            console.log('Bouton précédent cliqué');
        });
    
        $('.carousel-control-next').on('click', function() {
            console.log('Bouton suivant cliqué');
            i = i + 1;
            if (i >= 5) {
                startCountdown.disabled = false;
            }
        });


const slides = [
    {
        "image": "./app/accueil/assets/plateforme.JPG",
        "texte": "Le but de se test est d'évaluer votre équilibre.\n\nLa capacité à se tenir en équilibre sur une jambe est essentielle à une locomotion normale et est déterminante pour les activités de la vie quotidienne telles que se tourner , monter les escaliers et s'habiller.\n\nNous allons utiliser cette plateforme pour évaluer votre équilibre. Vous allez devoir effectuer un passage par jambe."
    },
    {
        "image": "./app/accueil/assets/equilibre.png",
        "secondImage": "./app/accueil/assets/equilibreDetail.png",
        "texte": 
        `<div>
            <p>Il n'existe qu'une seule bonne position pour la réalisation de ce test.</p>
            <p>La bonne position correspond à l'image suivante.</p>
            <p>Les consignes à respecter:</p>
            <ul>
                <li>Placer les mains sur les hanches</li>
                <li>Lever une jambe. Celle-ci ne doit pas toucher la plateforme et ne pas prendre appui sur l'autre jambe.</li>
            </ul>
            <p>Essayer la position pendant 5 secondes avant de commencer le test.</p>
        </div>
        `
    },    
    {
        "image": "./app/accueil/assets/mauvaisePosture1.png",
        "secondImage": "./app/accueil/assets/mauvaisePosture1Detail.png",
        "texte": 
        `<div>
            <p>Exemple de position ne respectant pas les consignes ! </p>
            <p>Contact entre les jambes.</p>

        </div>`
    },
    {
        "image": "./app/accueil/assets/mauvaisePosture2.png",
        "texte": 
        `<div>
            <p>Autre exemple de position ne respectant pas les consignes ! </p>
            <p>Contact avec la plateforme.</p>

        </div>`
    },
    {
        "image": "./app/accueil/assets/mauvaisePosture2.png",
        "texte": 
        `<div>
            <p>Déroulement du test : </p>
            <ul>
                <li>Montez sur la plateforme avec les 2 jambes.</li>
                <li>Quand vous êtes prêt, levez la jambe gauche, le test va démarrer automatiquement.</li>
                <li>Fixez ensuite le point bleu sur l'écran durant les 15 secondes du test.</li>
                <li>Lorsque les 15 secondes sont terminées, vous avez 15 secondes de récupération.</li>
                <li>Vous pourrez alors lever la jambe droite pour démarrer la 2ème phase du test.</li>

        </div>`
    }
];
    
const carouselInner = document.querySelector('.carousel-inner');
window.idUserSelected = 0;


slides.forEach((slide, index) => {
    const activeClass = index === 0 ? 'active' : '';

    let secondImageHTML = '';
    if(slide.secondImage) {
        secondImageHTML = `<img src="${slide.secondImage}" class="d-block custom-img second-img" alt="Seconde image ${index + 1}" style="position: absolute; z-index:2">`;
    }

    carouselInner.innerHTML += `
        <div class="carousel-item ${activeClass}">
            <div class="row">
                <div class="col-md-6 d-flex justify-content-center align-items-center" style="position: relative;">
                    <img src="${slide.image}" class="d-block custom-img" alt="Image ${index + 1}" style="height: auto; position:absolute; z-index:1">
                    ${secondImageHTML}
                </div>
                <div class="col-md-6 d-flex justify-content-center align-items-center">
                    <p>${slide.texte}</p>
                </div>
            </div>
        </div>
    `;
});

    
    



function handleStartCountdownClick() {
    console.log('run test');
    document.getElementById('overlay2').classList.add('active');
    startCountdown.disabled = true;
    const payload = {
        'topic': 'toPython',
        'status': 'start',
        'essai': 100,
        'idUser': window.idUserSelected
    };
    window.api.send('toMain', payload);
}

// Supprimez d'abord le précédent écouteur d'événement (s'il existe)
startCountdown.removeEventListener('click', handleStartCountdownClick);

// Ensuite, ajoutez le nouvel écouteur d'événement
startCountdown.addEventListener('click', handleStartCountdownClick);


loadUserData();
toggleOffset();

function toggleOffset() {
    payload = {
        topic: 'toPython',
        status: 'offset'
    }
    window.api.send('toMain',payload);

}

function loadUserData() {
    console.log('load user data');
    payload = {
        topic: 'get-users',
        message: ''
    }
    window.api.send('toMain', payload);
}
    
window.api.receive('fromMain', (arg) => {
    if (arg.type === 'get-users-reply') {
    let userSelect = document.getElementById('userSelect');

    // Vider l'élément 'select' à chaque nouvel appel
    userSelect.innerHTML = "Choisir l'utilisateur";

    // Ajouter une option par défaut
    let defaultOption = document.createElement('option');
    defaultOption.textContent = 'Choisir l\'utilisateur';
    defaultOption.selected = true;
    defaultOption.disabled = true;
    userSelect.appendChild(defaultOption);

    arg.data.forEach(user => {
        let option = document.createElement('option');
        option.value = user.id;  
        option.nom = user.prenom;
        option.textContent = user.prenom + ' (ID: ' + user.id + ')'; 
        userSelect.appendChild(option);
    });
    }

    if (arg.status == 'onPlateform' && userTest == false) {
        console.log('on');
        const messageUser = document.getElementById('messageUser');
        messageUser.textContent = "Restez immobile sur la plateforme durant quelques secondes";

        const payload = {
            'topic': 'toPython',
            'status': 'wait',
            'essai': 50,
            'baseline': true
        }
        window.api.send('toMain', payload);
        
                // RESTEZ IMMOBILE 3 SECONDES 
       //Attendre 3 secondes avant d'envoyer le message
        setTimeout(() => {


            const payload = {
                'topic': 'toPython',
                'status': 'wait',
                'essai': 50,
                'baseline': false
            };
            window.api.send('toMain', payload);
            userTest = true;  // Assurez-vous d'affecter la nouvelle valeur avec '=' et non '=='
        }, 3000);





    }
});

function handleUserSelectChange(event) {
    document.getElementById('bonjour').textContent = 'Bonjour ' + event.target.selectedOptions[0].nom + ' !';
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('changeUser').style.display = 'block';
    window.idUserSelected = event.target.value;
    const payload = {
        topic: 'user-selected',
        message: window.idUserSelected
    };
    window.api.send('toMain', payload);
}

const userSelect = document.getElementById('userSelect');

// Supprimez d'abord le précédent écouteur d'événement (s'il existe)
userSelect.removeEventListener('change', handleUserSelectChange);

// Ensuite, ajoutez le nouvel écouteur d'événement
userSelect.addEventListener('change', handleUserSelectChange);
    
document.getElementById('changeUser').addEventListener('click', () => {
    document.getElementById('overlay').style.display = 'flex';
    document.getElementById('changeUser').style.display = 'none';


})
    
    


})