var data;
var players_created = false;
var chosen_cards = [];
demand = null;
//TODO: correct the naming of css classes
function getCookie(name) { //For the CSRF token
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submit_move(draw) {
    //sends a POST request with chosen_cards to the move view
    //the draw parameter indicates whether or not to draw cards instead of throwing them
    let req = new XMLHttpRequest();
    let csrftoken = getCookie('csrftoken');

    req.open("POST", "move", true)
    req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    req.setRequestHeader('X-CSRFToken', csrftoken)

    if (draw) {
        req.send("throws=draw")
    }
    else {
        req.send("throws=" + JSON.stringify(chosen_cards) + ";demand=" + JSON.stringify(demand));
    }
}

function card_to_name(card) {
    //returns a string with a human-friendly represantation of the card
    let suits = ['&#9827;', '&#9829;', '&#9824;', '&#9830;']; //unicode for clubs, hearts, spades and diamonds (CHaSeD order)
    let values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

    //card numbers go in CHSD order, so 1 to 13 are ace to king of clubs, 14 is the ace of hearts and so on 
    suit = Math.ceil(card / 13) - 1; //-1 for the arr indexes and for the suit*13 to work
    value = card - suit * 13 - 1;

    return values[value] + suits[suit];
}

function create_players(state) {
    /*
        Creates player divs
    */
    let grid = document.getElementById('grid-game_players');

    for (let i = 0; i < state.player_count - 1; i++) {
        grid.innerHTML += "<div class='player'>" + "<div class='player_title'>player " + (i + 1).toString() + "</div><div class='player-cards playingCards'></div></div>&#13";
    }

}

function update_info(state) {
    let game_top_cards = document.getElementById("game_top_cards");
    let game_special_state = document.getElementById("game_special_state");

    game_top_cards.innerHTML = "Top card: " + card_to_name(state.top_cards);

    let special = state.special;
    let color_demands = [-20, -30, -40, -50];
    if (special == 0) game_special_state.innerHTML = "No battle/demand"
    else if (special > 0) game_special_state.innerHTML = "Battle: " + special.toString() + " to be drawn";
    else if (special < 0 && special > -14) game_special_state.innerHTML = "Demand: " + special.toString();
    else {
        let suits = ['&#9827;', '&#9829;', '&#9824;', '&#9830;']; //unicode for clubs, hearts, spades and diamonds (CHaSeD order)
        //-2 to adjust both for indexes and the -20,-30,-40,-50 scheme
        console.log(special);
        console.log((-special) / 10 - 2)

        game_special_state.innerHTML = "Demand: " + suits[(-special) / 10 - 2];
    }

}

function update_active_player(state) {
    //add the "game-active" class to a player/user div and removes it from everybody else
    let user = document.getElementById("game_user_hand");
    let players = document.getElementsByClassName("player");

    user.classList.remove("game-active");

    for (let i = 0; i < players.length; i++) players[i].classList.remove("game-active");

    if (state.active_player == state.position) {
        user.classList.add("game-active");
    }
    else {
        let player = state.position + 1;
        if (player >= state.player_count) player = 0;
        console.log(players.length)
        for (let i = 0; i < players.length; i++) {
            console.log('dddd')

            if (state.active_player + i == player) {
                players[i].classList.add("game-active");
                break;
            }

        }

    }

}

function update_demands() {
    function print_demands(type) {

        let demands_div = document.getElementById("game_demands");
        demands_div.classList.remove("empty");
        demands_div.innerHTML = "<h1>Your demand: </h1>";
        let demands;
        let human_values;
        if (type == 'aces') {
            demands = [1, 2, 3, 4];
            human_values = ['&#9827;', '&#9829;', '&#9824;', '&#9830;'];

        }
        else if (type == "jacks") { //for jacks
            //TODO: decide wheter or not queens can be demanded (also in views.move)
            demands = [5, 6, 7, 8, 9, 10, 12];
            human_values = ['5', '6', '7', '8', '9', '10', 'Q'];
        }
        console.log(human_values.length)
        for (let i = 0; i < human_values.length; i++) {
            demands_div.innerHTML += "<div class='demand'>" + human_values[i] + "</div>&#13";
        }
        let divs = document.getElementsByClassName('demand');
        for (let i = 0; i < divs.length; i++) {
            divs[i].addEventListener("click", function (event) {
                let div = event.target;
                demand = null;
                if (div.matches(".demand-toggled")) {
                    div.classList.remove("demand-toggled");
                }
                else {
                    for (let j = 0; j < divs.length; j++) divs[j].classList.remove("demand-toggled");
                    div.classList.add("demand-toggled");
                    demand = demands[i];
                }
            });
        }
    }
    jacks = [11, 24, 37, 50];
    aces = [1, 14, 27, 40];
    for (let i = 0; i < 4; i++) {
        if (chosen_cards.some(card => card == jacks[i])) {
            print_demands("jacks")
            break;
        }
        else if (chosen_cards.some(card => card == aces[i])) {

            print_demands("aces")
            break;
        }
        if (i == 3) {
            let demands_div = document.getElementById("game_demands");
            demands_div.innerHTML = "";
            demands_div.classList.add("empty");
            console.log('xd');
        }
    }
}

function update_cards(state) { //TODO: visually represent cards/their amount of each player 
    //TODO: add some checks so only same-value cards can be added to the chosen_cards
    chosen_cards = [];
    console.log(state)
    let players = document.getElementsByClassName("player-cards");
    let user = document.getElementById("game_user_cards");
    let current_seat = 0; //the seat that we're updating the cards for

    for (let i = 0; i < state.player_count; i++) {
        if (i == state.position) {
            user.innerHTML = "";

            for (let j = 0; j < state.hands[i].length; j++) {
                user.innerHTML += "<div class='user-card'>" + card_to_name(state.hands[i][j]) + "</div>&#13";
            }
        }
        else {

            players[current_seat].innerHTML = "";
            for (let j = 0; j < state.hands[i]; j++) players[current_seat].innerHTML += "<div class='card back player-card'>*</div>"; //TODO: change to a visual repres. of a card
            current_seat++;
        }
    }
    let user_cards = document.getElementsByClassName("user-card");

    for (let i = 0; i < user_cards.length; i++) user_cards[i].addEventListener("click", function (event) {
        let card = event.target;
        if (card.matches(".card-toggled")) {
            card.classList.remove("card-toggled");
            chosen_cards.splice(chosen_cards.indexOf(state.hands[state.position][i]), 1);
        }
        else {
            card.classList.add("card-toggled");
            chosen_cards.push(state.hands[state.position][i]);
        }
        update_demands();
    });
}

async function update_json() {
    fetch("state")
        .then(resp => resp.json())
        .then(resp => {
            if (data == undefined || data.move_count != resp.move_count) {
                data = resp;
                if (!players_created) {
                    create_players(data);
                    players_created = true;
                }
                update_cards(data);
                update_active_player(data);
                update_info(data);

            }

        });
    await new Promise(r => setTimeout(r, 1000)); //apparently async is now the optimal way to do a "sleep"
    update_json();
}

update_json();



