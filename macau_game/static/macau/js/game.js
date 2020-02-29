var data;
var players_created = false;

function card_to_name(card) {
    //returns a string with a human-friendly represantation of the card
    suits = ['&#9827;', '&#9829;', '&#9824;', '&#9830;']; //unicode for clubs, hearts, spades and diamonds (CHaSeD order)
    values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

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
        grid.innerHTML += "<div class='player'>" + "player " + (i + 1).toString() + "<div class='player-cards'></div></div>&#13";
    }

}

function active_player(state) {
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
        for (let i = 0; i < players.length; i++) {
            if (state.active_player + i == player) {
                players[i].classList.add("game-active");
                break;
            }
            else if (state.active_player + i >= state.player_count) {
                player = 0;
            }
        }

    }

}


function update_cards(state) { //TODO: visually represent cards/their amount of each player 
    let players = document.getElementsByClassName("player-cards");
    console.log(players.length);
    let user = document.getElementById("game_user_hand");
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
            for (let j = 0; j < state.hands[i]; j++) players[current_seat].innerHTML += "c"; //TODO: change to a visual repres. of a card
            current_seat++;
        }
    }
}

async function update_json() {
    fetch("state")
        .then(resp => resp.json())
        .then(resp => {
            if (data != resp) {
                data = resp;
                if (!players_created) {
                    create_players(data);
                    players_created = true;
                }
                update_cards(data);
                active_player(data);
                console.log(JSON.stringify(data)); //TODO: remove after the view is done
            }

        });
    await new Promise(r => setTimeout(r, 1000)); //apparently async is now hte optimal way to do a "sleep"
    update_json();
}

update_json();



