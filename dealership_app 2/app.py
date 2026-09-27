# app.py
from flask import Flask
from blueprints.auth        import auth_bp
from blueprints.dashboard   import dashboard_bp
from blueprints.customers   import customers_bp
from blueprints.vehicles    import vehicles_bp
from blueprints.sales       import sales_bp
from blueprints.service     import service_bp
from blueprints.loans       import loans_bp
from blueprints.accounting  import accounting_bp
from blueprints.reports     import reports_bp
from blueprints.admin       import admin_bp

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_secure_random_string'

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(service_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(accounting_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
