$(document).ready(function() {
    $('#username-form').on('submit', function(event) {
        event.preventDefault();
        const username = $('#username').val();

        $('#loading').show();
        $('#results').hide();
        $('#error').hide();

        $.ajax({
            url: `/api/roster/${username}`,
            method: 'GET',
            success: function(data) {
                $('#loading').hide();
                $('#display-username').text(data.user.username);

                // Populate team rankings
                const teamRankingDiv = $('#team-ranking');
                teamRankingDiv.empty();
                let table = '<table class="table table-striped"><thead><tr><th>Rank</th><th>Team</th><th>Score</th></tr></thead><tbody>';
                data.team_ranking.forEach((team, index) => {
                    table += `<tr><td>${index + 1}</td><td>${team.team}</td><td>${team.score.toFixed(2)}</td></tr>`;
                });
                table += '</tbody></table>';
                teamRankingDiv.html(table);

                // Populate detailed roster
                const detailedRosterDiv = $('#detailed-roster');
                detailedRosterDiv.empty();
                let rosterTable = '<table class="table table-sm"><thead><tr><th>Player</th><th>Team</th><th>Position</th><th>Leagues</th></tr></thead><tbody>';
                data.roster.forEach(player => {
                    let leagues = player.leagues.map(l => `${l.league_name} (${l.status})`).join(', ');
                    rosterTable += `<tr><td>${player.full_name}</td><td>${player.team}</td><td>${player.position}</td><td>${leagues}</td></tr>`;
                });
                rosterTable += '</tbody></table>';
                detailedRosterDiv.html(rosterTable);

                $('#results').show();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#loading').hide();
                const errorMsg = jqXHR.responseJSON ? jqXHR.responseJSON.error : 'An unknown error occurred.';
                $('#error').text(errorMsg).show();
            }
        });
    });
});
