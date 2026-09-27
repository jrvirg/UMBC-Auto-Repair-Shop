# blueprints/dashboard.py
from flask import Blueprint, render_template, session
from utils import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
                           username=session.get('username'),
                           job=session.get('job'),
                           division_id=session.get('division_id'))
