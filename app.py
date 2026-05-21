import streamlit as st
import pandas as pd

CATEGORY_BASE_POINT = {
    "Gold": 150,
    "Silver": 80,
    "Bronze": 50
}

# ==========================================
# PART 1: THE BRAIN (Rules and Logic)
# ==========================================

class Tournament:
    def __init__(self, name):
        self.name = name
        self.logo = None
        self.teams = []
        self.player_pool = []
        self.auction_log = []
    
    def set_logo(self, logo_bytes):
        self.logo = logo_bytes
    
    def add_team(self, team):
        if team not in self.teams:
            self.teams.append(team)
    
    def remove_team(self, team_name):
        self.teams = [t for t in self.teams if t.name != team_name]

class Team:
    MAX_GOLD = 3
    MAX_SILVER = 3
    MAX_BRONZE = 2
    SILVER_RESERVE = 80
    BRONZE_RESERVE = 50

    def __init__(self, name):
        self.name = name
        self.purse = 1000
        self.gold_players = 0
        self.silver_players = 0
        self.bronze_players = 0
        self.logo = None

    def set_logo(self, logo_bytes):
        self.logo = logo_bytes

    def reserve_budget_after_purchase(self, category=None):
        """Reserve enough budget for mandatory future slots after this purchase."""
        remaining_gold = max(0, self.MAX_GOLD - self.gold_players - (1 if category == "Gold" else 0))
        remaining_silver = max(0, self.MAX_SILVER - self.silver_players - (1 if category == "Silver" else 0))
        remaining_bronze = max(0, self.MAX_BRONZE - self.bronze_players - (1 if category == "Bronze" else 0))

        return (
            remaining_gold * CATEGORY_BASE_POINT["Gold"] +
            remaining_silver * CATEGORY_BASE_POINT["Silver"] +
            remaining_bronze * CATEGORY_BASE_POINT["Bronze"]
        )

    def get_max_bid(self, category="Gold"):
        return max(0, self.purse - self.reserve_budget_after_purchase(category))

    def has_slot_for(self, category):
        if category == "Gold":
            return self.gold_players < self.MAX_GOLD
        if category == "Silver":
            return self.silver_players < self.MAX_SILVER
        if category == "Bronze":
            return self.bronze_players < self.MAX_BRONZE
        return False

    def buy_player(self, category, bid):
        self.purse -= bid
        if category == "Gold":
            self.gold_players += 1
        elif category == "Silver":
            self.silver_players += 1
        elif category == "Bronze":
            self.bronze_players += 1

    def to_dict(self):
        return {
            "Team Name": self.name,
            "Purse": self.purse,
            "Gold": self.gold_players,
            "Silver": self.silver_players,
            "Bronze": self.bronze_players,
            "Max Gold Bid": self.get_max_bid("Gold"),
            "Max Silver Bid": self.get_max_bid("Silver"),
            "Max Bronze Bid": self.get_max_bid("Bronze")
        }


def create_empty_teams():
    return []

if "tournaments" not in st.session_state:
    st.session_state.tournaments = {}

if "active_tournament" not in st.session_state:
    st.session_state.active_tournament = None

if "teams" not in st.session_state:
    st.session_state.teams = create_empty_teams()

if "auction_log" not in st.session_state:
    st.session_state.auction_log = []

if "player_pool" not in st.session_state:
    st.session_state.player_pool = []


def get_category_min_bid(category):
    return CATEGORY_BASE_POINT.get(category, 50)


def get_tournament_teams():
    if st.session_state.active_tournament and st.session_state.active_tournament in st.session_state.tournaments:
        return st.session_state.tournaments[st.session_state.active_tournament].teams
    return st.session_state.teams


def get_tournament_player_pool():
    if st.session_state.active_tournament and st.session_state.active_tournament in st.session_state.tournaments:
        return st.session_state.tournaments[st.session_state.active_tournament].player_pool
    return st.session_state.player_pool


def get_tournament_auction_log():
    if st.session_state.active_tournament and st.session_state.active_tournament in st.session_state.tournaments:
        return st.session_state.tournaments[st.session_state.active_tournament].auction_log
    return st.session_state.auction_log


def get_available_players():
    pool = get_tournament_player_pool()
    return [player for player in pool if player["Status"] == "Available"]


def add_player_to_pool(name, category, custom_base=None):
    cap = custom_base if custom_base is not None else get_category_min_bid(category)
    pool = get_tournament_player_pool()
    pool.append({
        "Name": name.strip(),
        "Category": category,
        "Base Price": cap,
        "Salary Cap": cap,
        "Status": "Available"
    })


def update_player_in_pool(index, name, category, custom_base=None):
    pool = get_tournament_player_pool()
    player = pool[index]
    player["Name"] = name.strip()
    player["Category"] = category
    cap = custom_base if custom_base is not None else get_category_min_bid(category)
    player["Base Price"] = cap
    player["Salary Cap"] = cap


def remove_player_from_pool(index):
    pool = get_tournament_player_pool()
    pool.pop(index)


def mark_player_assigned(index):
    pool = get_tournament_player_pool()
    pool[index]["Status"] = "Assigned"


def reset_auction():
    teams = get_tournament_teams()
    teams.clear()
    get_tournament_auction_log().clear()
    get_tournament_player_pool().clear()
    st.experimental_rerun()


def add_team_to_tournament(team_name):
    teams = get_tournament_teams()
    if not any(t.name == team_name.strip() for t in teams):
        teams.append(Team(team_name.strip()))
        return True
    return False

# ==========================================
# PART 2: THE FACE (User Interface / Web Page)
# ==========================================

st.title("🏏 Cricket Auction App")
st.write("Manage unlimited team auctions with category rules, budgets, and history.")

st.markdown("---")

st.subheader("Tournament Management")
with st.expander("Create or Select Tournament"):
    tour_col1, tour_col2 = st.columns([2, 1])
    with tour_col1:
        new_tournament_name = st.text_input("New Tournament Name", placeholder="e.g. IPL 2026", key="new_tournament_name")
        if st.button("Create Tournament"):
            if not new_tournament_name.strip():
                st.error("Enter a tournament name.")
            elif new_tournament_name.strip() in st.session_state.tournaments:
                st.error("Tournament already exists.")
            else:
                tournament = Tournament(new_tournament_name.strip())
                st.session_state.tournaments[new_tournament_name.strip()] = tournament
                st.session_state.active_tournament = new_tournament_name.strip()
                st.success(f"Created tournament: {new_tournament_name.strip()}. Add teams below.")
    
    with tour_col2:
        tournament_names = list(st.session_state.tournaments.keys())
        if tournament_names:
            selected_tournament = st.selectbox(
                "Select Tournament",
                tournament_names,
                index=tournament_names.index(st.session_state.active_tournament) if st.session_state.active_tournament in tournament_names else 0,
                key="tournament_select"
            )
            if st.button("Activate Tournament"):
                st.session_state.active_tournament = selected_tournament
                st.success(f"Activated: {selected_tournament}")
        else:
            st.write("No tournaments yet. Create one above.")
    
    if st.session_state.active_tournament and st.session_state.active_tournament in st.session_state.tournaments:
        active_tour = st.session_state.tournaments[st.session_state.active_tournament]
        st.write(f"**Active Tournament:** {active_tour.name}")
        
        st.write("**Upload Tournament Logo**")
        tour_logo_file = st.file_uploader(
            "Upload logo for this tournament",
            type=["png", "jpg", "jpeg"],
            key="tournament_logo_upload"
        )
        if tour_logo_file is not None:
            active_tour.set_logo(tour_logo_file.read())
            st.success(f"Uploaded logo for {active_tour.name}.")
        
        if active_tour.logo is not None:
            st.image(active_tour.logo, width=150, caption=f"{active_tour.name} Logo")
        
        st.write("**Manage Teams in Tournament**")
        team_col1, team_col2 = st.columns([2, 1])
        with team_col1:
            new_team_name = st.text_input("Add new team name", placeholder="e.g. Mumbai Indians", key="new_team_name_input")
            if st.button("Add Team"):
                if not new_team_name.strip():
                    st.error("Enter a team name.")
                elif add_team_to_tournament(new_team_name):
                    st.success(f"Added team: {new_team_name.strip()}")
                else:
                    st.error(f"Team '{new_team_name.strip()}' already exists in this tournament.")
        
        with team_col2:
            teams_list = get_tournament_teams()
            if teams_list:
                team_to_remove = st.selectbox("Remove team", [t.name for t in teams_list], key="remove_team_select")
                if st.button("Remove Team"):
                    active_tour.remove_team(team_to_remove)
                    st.success(f"Removed team: {team_to_remove}")
        
        st.write(f"**Teams in this tournament:** {len(active_tour.teams)}")

st.markdown("---")

st.subheader("Live Team Standings")
teams = get_tournament_teams()
if len(teams) == 0:
    st.warning("No teams added to the active tournament yet. Add teams in the Tournament Management section.")
else:
    logo_cols = st.columns(len(teams))
    for idx, team in enumerate(teams):
        with logo_cols[idx]:
            if team.logo is not None:
                st.image(team.logo, use_column_width=True, caption=team.name)
            else:
                st.markdown(f"**{team.name}**")
                st.write("No logo uploaded")

    team_data = [team.to_dict() for team in teams]
    team_df = pd.DataFrame(team_data)
    st.dataframe(team_df, use_container_width=True)

with st.expander("Auction Rules"):
    st.write(
        "- Each team starts with a purse of 1000 points.\n"
        "- Each team can buy up to 3 Gold, 3 Silver, and 2 Bronze players.\n"
        "- When bidding, teams must reserve budget for remaining mandatory slots.\n"
        "- Gold bids reserve funds for future Silver and Bronze slots; Silver bids reserve Bronze slots.\n"
        "- Manage unlimited teams within each tournament."
    )

st.markdown("---")

st.subheader("Player Pool")
with st.expander("Add and Edit Players"):
    new_player_name = st.text_input("New player name", placeholder="e.g. Rohit Sharma", key="new_player_name")
    new_player_category = st.selectbox("New player category", ["Gold", "Silver", "Bronze"], key="new_player_category")
    new_player_base = get_category_min_bid(new_player_category)
    st.write(f"Default minimum base points for {new_player_category} is {new_player_base}.")
    custom_base_input = st.number_input(
        "Custom Base Point (leave as default or set custom value)",
        min_value=10,
        step=10,
        value=new_player_base,
        key="new_player_custom_base"
    )
    if st.button("Add Player to Pool"):
        if not new_player_name.strip():
            st.error("Enter a player name before adding.")
        else:
            add_player_to_pool(new_player_name, new_player_category, custom_base_input)
            st.success(f"Added {new_player_name.strip()} ({new_player_category}) with base point {custom_base_input}.")

    pool = get_tournament_player_pool()
    if pool:
        edit_options = [f'{player["Name"]} ({player["Category"]}) - {player["Status"]}' for player in pool]
        selected_edit = st.selectbox("Select player to edit or remove", edit_options, key="player_edit_select")
        selected_index = edit_options.index(selected_edit)
        selected_player = pool[selected_index]

        edit_name = st.text_input(
            "Edit player name",
            value=selected_player["Name"],
            key=f"edit_player_name_{selected_index}"
        )
        edit_category = st.selectbox(
            "Edit player category",
            ["Gold", "Silver", "Bronze"],
            index=["Gold", "Silver", "Bronze"].index(selected_player["Category"]),
            key=f"edit_player_category_{selected_index}"
        )
        edit_base = get_category_min_bid(edit_category)
        st.write(f"Default minimum base points for {edit_category} is {edit_base}.")
        edit_custom_base = st.number_input(
            "Edit Base Point (salary cap)",
            min_value=10,
            step=10,
            value=selected_player.get("Salary Cap", edit_base),
            key=f"edit_player_custom_base_{selected_index}"
        )

        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            if st.button("Update Player"):
                if not edit_name.strip():
                    st.error("Player name cannot be empty.")
                else:
                    update_player_in_pool(selected_index, edit_name, edit_category, edit_custom_base)
                    st.success("Player updated.")
        with col_edit2:
            if st.button("Remove Player"):
                remove_player_from_pool(selected_index)
                st.success("Player removed.")
    else:
        st.write("No players in the pool yet. Add one above.")

st.write("### Current Player Pool")
pool = get_tournament_player_pool()
if pool:
    pool_df = pd.DataFrame(pool)
    st.dataframe(pool_df, use_container_width=True)
else:
    st.write("No players added to the pool yet.")

st.markdown("---")

with st.expander("Team Settings"):
    st.write("Manage team names, purses, and logos.")
    teams_list = get_tournament_teams()
    
    if teams_list:
        team_edit_select = st.selectbox("Select team to edit", [t.name for t in teams_list], key="team_edit_select")
        selected_team_idx = next((i for i, t in enumerate(teams_list) if t.name == team_edit_select), 0)
        selected_team = teams_list[selected_team_idx]
        
        st.write(f"### Edit: {selected_team.name}")
        
        team_col1, team_col2 = st.columns(2)
        with team_col1:
            edited_team_name = st.text_input(
                "Team Name",
                value=selected_team.name,
                key=f"edit_team_name_{selected_team_idx}"
            )
        with team_col2:
            edited_team_purse = st.number_input(
                "Team Purse",
                min_value=0,
                max_value=5000,
                step=10,
                value=selected_team.purse,
                key=f"edit_team_purse_{selected_team_idx}"
            )
        
        if st.button("Update Team Name & Purse"):
            selected_team.name = edited_team_name
            selected_team.purse = edited_team_purse
            st.success(f"Updated {edited_team_name} with purse {edited_team_purse}.")
        
        st.write(f"### Logo for {selected_team.name}")
        if selected_team.logo is not None:
            st.image(selected_team.logo, width=120)
        logo_file = st.file_uploader(
            f"Upload or replace logo for {selected_team.name}",
            type=["png", "jpg", "jpeg"],
            key=f"team_logo_upload_{selected_team_idx}"
        )
        if logo_file is not None:
            selected_team.set_logo(logo_file.read())
            st.success(f"Uploaded logo for {selected_team.name}.")
        
        if st.button("Reset All Team Purses"):
            for team in teams_list:
                team.purse = 1000
            st.success("All team purses reset to 1000.")
    else:
        st.warning("No teams in this tournament. Add teams in the Tournament Management section.")

st.markdown("---")

st.subheader("Bidding Arena")
player_category_filter = st.selectbox(
    "Filter available players by category",
    ["All", "Gold", "Silver", "Bronze"],
    key="player_category_filter"
)
available_players = get_available_players()
if player_category_filter != "All":
    available_players = [p for p in available_players if p["Category"] == player_category_filter]

col1, col2 = st.columns([2, 1])
with col1:
    player_name = ""
    player_category = "Gold"
    selected_player = None
    selected_player_base = None
    selected_player_cap = None
    if available_players:
        available_labels = [f'{player["Name"]} ({player["Category"]})' for player in available_players]
        selected_label = st.selectbox("Select available player", available_labels, key="selected_player_label")
        selected_index = available_labels.index(selected_label)
        selected_player = available_players[selected_index]
        player_name = selected_player["Name"]
        player_category = selected_player["Category"]
        selected_player_base = selected_player["Base Price"]
        selected_player_cap = selected_player["Salary Cap"]
        st.write(f"Minimum bid: {selected_player_base}")
        st.write(f"Salary cap: {selected_player_cap}")
    else:
        st.warning("No available players in the pool. Add players before auctioning.")
        player_name = st.text_input("Player Name", placeholder="e.g. Virat Kohli")
        player_category = st.selectbox("Player Category", ["Gold", "Silver", "Bronze"])
        manual_base = get_category_min_bid(player_category)
        st.write(f"Minimum base points and salary cap for {player_category} is {manual_base}.")
        selected_player_cap = manual_base
    winning_bid = st.number_input("Winning Bid Amount", min_value=50, step=10, value=100)

with col2:
    teams_list = get_tournament_teams()
    team_names = [team.name for team in teams_list]
    winning_team_name = st.selectbox("Winning Team", team_names)
    st.write("### Team Budget Guidance")
    selected_team = next((team for team in teams_list if team.name == winning_team_name), None)
    if selected_team:
        st.write(f"- Max Gold Bid: {selected_team.get_max_bid('Gold')}")
        st.write(f"- Max Silver Bid: {selected_team.get_max_bid('Silver')}")
        st.write(f"- Max Bronze Bid: {selected_team.get_max_bid('Bronze')}")
        st.write(
            f"- Remaining slots: Gold {selected_team.MAX_GOLD - selected_team.gold_players}, "
            f"Silver {selected_team.MAX_SILVER - selected_team.silver_players}, "
            f"Bronze {selected_team.MAX_BRONZE - selected_team.bronze_players}"
        )

process = st.button("Process Purchase")
reset = st.button("Reset Auction")

if reset:
    reset_auction()

if process:
    if not player_name.strip():
        st.error("Please enter a player name before processing the purchase.")
    else:
        teams_list = get_tournament_teams()
        team = next((team for team in teams_list if team.name == winning_team_name), None)
        if not team:
            st.error("Selected team not found.")
        elif not team.has_slot_for(player_category):
            st.error(f"❌ {team.name} cannot buy more {player_category} players.")
        else:
            base_price = selected_player["Base Price"] if selected_player is not None else get_category_min_bid(player_category)
            salary_cap = selected_player["Salary Cap"] if selected_player is not None else selected_player_cap
            max_bid = team.get_max_bid(player_category)
            if winning_bid < base_price:
                st.error(f"❌ Bid must be at least {base_price} for {player_category} players.")
            elif winning_bid > salary_cap:
                st.error(f"❌ Bid exceeds the player's salary cap of {salary_cap}.")
            elif winning_bid > max_bid:
                st.error(
                    f"❌ Transaction Failed! {team.name} must reserve budget for required future slots. "
                    f"Max allowed for {player_category} is {max_bid}."
                )
            else:
                team.buy_player(player_category, winning_bid)
                if selected_player is not None:
                    pool = get_tournament_player_pool()
                    pool_index = pool.index(selected_player)
                    mark_player_assigned(pool_index)
                log_entry = {
                    "Player": player_name,
                    "Category": player_category,
                    "Team": team.name,
                    "Bid": winning_bid,
                    "Base Price": base_price,
                    "Salary Cap": salary_cap
                }
                get_tournament_auction_log().append(log_entry)
                st.success(f"✅ Sold! {player_name} goes to {team.name} for {winning_bid} points.")

st.markdown("---")

st.subheader("Auction History")
auction_log = get_tournament_auction_log()
if auction_log:
    history_df = pd.DataFrame(auction_log)
    st.table(history_df)
else:
    st.write("No auctions processed yet.")
