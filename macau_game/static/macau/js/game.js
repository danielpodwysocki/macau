var data;

function update_cards(json) { //TODO: visually represent cards/their amount of each player 

}


async function update_json() {
    fetch("state")
        .then(resp => resp.json())
        .then(resp => {
            if (data != resp) {
                data = resp;
                update_cards(data);
                console.log(JSON.stringify(data));
            }

        });
    await new Promise(r => setTimeout(r, 1000)); //apparently async is now hte optimal way to do a "sleep"
    update_json();
}

update_json();



