function updateStats() {
    const stats = {
        total_wins: document.getElementById('total-wins').value,
        total_losses: document.getElementById('total-losses').value,
        assaults_won: document.getElementById('assaults-won').value,
        assaults_lost: document.getElementById('assaults-lost').value,
        defending_battles_won: document.getElementById('defending-battles-won').value,
        defending_battles_lost: document.getElementById('defending-battles-lost').value,
        kills: document.getElementById('kills').value,
        destroyed_traps: document.getElementById('destroyed-traps').value,
        lost_associates: document.getElementById('lost-associates').value,
        lost_traps: document.getElementById('lost-traps').value,
        healed_associates: document.getElementById('healed-associates').value,
        wounded_enemy_associates: document.getElementById('wounded-enemy-associates').value,
        enemy_turfs_destroyed: document.getElementById('enemy-turfs-destroyed').value,
        turf_destroyed_times: document.getElementById('turf-destroyed-times').value,
        eliminated_enemy_influence: document.getElementById('eliminated-enemy-influence').value
    };

    fetch('/stats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(stats),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        getStats();
    })
    .catch(error => console.error('Error:', error));
}

function getStats() {
    fetch('/stats')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
        } else {
            updateStatsDisplay(data);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateStatsDisplay(stats) {
    for (const [key, value] of Object.entries(stats)) {
        const element = document.getElementById(key.replace(/_/g, '-'));
        if (element) {
            element.textContent = value;
        }
    }
}

// Call getStats when the page loads
document.addEventListener('DOMContentLoaded', getStats);
