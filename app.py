from flask import Flask, render_template, redirect, request, url_for, flash
from psycopg2.errors import UniqueViolation
from time import sleep

from utils.database_connection import DatabaseConnection
from utils.tournament_manager import TournamentManager

app = Flask(__name__)
app.secret_key = "just a dummy key"


# try:
#     # Connection to Database | DatabaseConnection as context manager
#     with DatabaseConnection() as connection:
#
#         cursor = connection.cursor()
#
#         cursor.execute("SELECT version();")
#         record = cursor.fetchone()
#
#         print("You are connected to - ", record, "\n")
#
# except (Exception, psycopg2.Error) as error:
#     print("Error while connecting to Database", error)


INSTITUTIONS = {
    'ZUT': 'Zambia University of Technology',
    'ZAST': 'Zambia Air Services Training',
    'NORTEC': 'Northern Technical College',
    'EVHONE': 'Evelyn Hone College',
    'LBTC': 'Lusaka Business And Technical College',
    'NIC': 'Nkumbi International College',
    'LIBES': 'Livingstone institute of Business And Engineering Studies',
    'COTBC': 'Copperbelt Technical Business College',
    'MATTI': 'Mansa Trades Training institute',
    'MOTTI': 'Mongu Trades Training Institute',
    'CHTTI': 'Chipata Trades Training Institute',
    'SOTTI': 'Solwezi Trades Training Institute',
    'PETTI': 'Pemba Trades Training Institute',
    'KATTI': 'Kaoma Trades Training institute',
    'NCTTI': 'Nchanga Trades Training Institute',
    'KVTC': 'Kitwe Vocational Training Centre',
    'KIT': 'Kabwe Institue Of Technology',
    'LTBT': 'Luanshya Technical and business Training',
    'CHITTI': 'Chinsali Trades Training Institute',
    'ZIBST': 'Zambia Institute Of Business Studies and Technology',
    'MTC': 'Mufulira Technical College',
    'CU': 'Cavendish University',
    'CHRESO': 'Chreso University',
    'ZASTI': 'Zambia Air Services Training Institute'
}


def main() -> None:
    @app.route('/')
    def home():
        return render_template('./public/index.html')


    @app.route('/about')
    def about():
        return render_template('./public/about.html')


    @app.route('/inst_registration', methods=['GET', 'POST'])
    def add_institution():
        if request.method == 'POST':
            institution_name = request.form['Institution']
            institution_town = request.form['institution_town']

            record_to_insert = (institution_name, institution_town)

            try:
                with DatabaseConnection() as connect:
                    cur = connect.cursor()
                    cur.execute('SELECT * FROM institution')
                    if not cur.fetchall():
                        cur.execute("""
                        ALTER SEQUENCE public.institution_institution_id_seq RESTART WITH 1
                        """)

                    insert_query = """INSERT INTO institution(institution_name, institution_town ) VALUES(%s, %s)"""

                    cur.execute("""
                                SELECT setval('public.institution_institution_id_seq', 
                                (SELECT COALESCE(MAX(institution_id), 1) FROM institution))
                                """)

                    cur.execute(insert_query, record_to_insert)
                flash(f"{institution_name} successfully registered!", "success")

            except UniqueViolation as e:

                flash(f"{institution_name} is already registered!", "danger")
                # return render_template('./public/registration.html', INSTITUTIONS=INSTITUTIONS)

            return redirect(url_for('add_team'))
        else:
            return render_template('./public/registration.html', INSTITUTIONS=INSTITUTIONS)


    @app.route('/team_registration', methods=['GET', 'POST'])
    def add_team():
        if request.method == 'GET':
            return render_template('./public/team_register.html', INSTITUTIONS=INSTITUTIONS)
        else:
            team_name = request.form['team_name']
            institution = request.form['Institution']
            coach_name = request.form['coach']
            tournament_entry = request.form['tournament']

            with DatabaseConnection() as connect:
                cur = connect.cursor()
                cur.execute("SELECT * FROM coach")
                if not cur.fetchall():
                    cur.execute("ALTER SEQUENCE public.coach_coach_id_seq RESTART WITH 1")

                # noinspection PyBroadException
                try:
                    cur.execute(f"INSERT INTO coach(coach_name) VALUES('{coach_name}');")
                except:
                    # return f'Coach with name, ({coach_name}) already exists. Enter team details and Leave Blank'
                    pass

            try:
                with DatabaseConnection() as connect:
                    cur = connect.cursor()

                    cur.execute("""
                                SELECT setval('public.coach_coach_id_seq', 
                                (SELECT COALESCE(MAX(coach_id), 1) FROM coach))
                                """)

                    cur.execute(f"SELECT coach_id FROM coach WHERE coach_name='{coach_name}'")
                    coach_id = cur.fetchone()[0]

                    # noinspection PyBroadException
                    try:
                        cur.execute(f"SELECT institution_id FROM institution WHERE institution_name='{institution}'")
                        institution_id = cur.fetchone()[0]
                    except Exception:
                        return 'Institution Not Registered<br />Register Institution First Before Registering Team and Players'

                    cur.execute(f"SELECT tournament_id FROM tournament WHERE tournament_name='{tournament_entry}'")
                    tournament_id = cur.fetchone()[0]

                    # return f'{str(coach_id)}<br>{institution_id}<br>{tournament_id}'


                    record_to_insert = (team_name, institution_id, coach_id, tournament_id) # tournament_id -> 2
                    # #
                    insert_query = """INSERT INTO teams(team_name, institution_id, coach_id, tournament_id) VALUES(%s, %s, %s, %s)"""

                    cur.execute("SELECT * FROM teams")
                    if not cur.fetchall():
                        cur.execute("ALTER SEQUENCE public.teams_team_id_seq RESTART WITH 1")
                    try:
                        cur.execute(insert_query, record_to_insert)
                    except Exception as error:
                        print(error)
                        return f'The team with name {team_name} already exists'
            except Exception as e:
                return e
            return redirect(url_for('add_player'))

    # noinspection PyBroadException
    @app.route('/player_registration', methods=['GET', 'POST'])
    def add_player():
        if request.method == 'GET':
            return render_template('./public/player_registration.html')
        else:
            player_name = request.form['player']
            player_age = request.form['age']
            player_gender = request.form['gender']
            player_team = request.form['team']

            with DatabaseConnection() as connect:
                cur = connect.cursor()
                try:
                    cur.execute(f"SELECT team_id FROM teams WHERE team_name='{player_team}'")
                    team_id = cur.fetchone()[0]
                except Exception:
                    return f'<i>{player_team}</i> is not registered<br />Can&apos;t register player'

                record_to_insert = (player_name, team_id, player_gender, player_age)

                insert_query = """INSERT INTO players(player_name, team_id, player_gender, age) VALUES(%s, %s, %s, %s)"""
                cur.execute("SELECT * FROM players")
                if not cur.fetchall():
                    cur.execute("""
                    ALTER SEQUENCE public.players_player_id_seq RESTART WITH 1                
                    """)
                cur.execute(insert_query, record_to_insert)

                return redirect(url_for('add_player'))



    @app.route('/tournaments')
    def show_tournaments():
        pass


    @app.route('/tournaments/<int:tournament_id>')
    def tournament():
        pass


    @app.route('/sports')
    def sport():
        return render_template('./public/fixtures/index.html')


    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('./public/errors/404.html'), 404


if __name__ == '__main__':
    admin = TournamentManager()
    # admin.insert_tournament(('ZUT TNMT', '2024-12-16', '2024-12-28',))
    # admin.delete_tournament('Youth Tournament')
    main()
    app.run(debug=True)