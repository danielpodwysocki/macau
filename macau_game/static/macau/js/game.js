var data;
var players_created = false;

function create_players(state) {
    let grid = document.getElementById('grid-game_players');
    for (let i = 0; i < state.player_count - 1; i++) {
        grid.innerHTML += "<div class='player'>p</div>&#13";
    }

}

function update_cards(state) { //TODO: visually represent cards/their amount of each player 
    let players = document.getElementsByClassName("player");
    console.log(players.length);
    let user = document.getElementById("game_user_hand");
    let current_seat = 0; //the seat that we're updating the cards for

    for (let i = 0; i < state.player_count; i++) {
        if (i == state.position) {
            user.innerHTML = "";

            for (let j = 0; j < state.hands[i].length; j++) {
                user.innerHTML += state.hands[i][j] + " "; //TODO: translate it to human values
            }
        }
        else {

            players[current_seat].innerHTML = "";
            for (let j = 0; j < state.hands[i]; j++) players[current_seat].innerHTML += "c"; //TODO: change to a visual repres. of a card
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
                console.log(JSON.stringify(data)); //TODO: remove after the view is done
            }

        });
    await new Promise(r => setTimeout(r, 1000)); //apparently async is now hte optimal way to do a "sleep"
    update_json();
}

update_json();



