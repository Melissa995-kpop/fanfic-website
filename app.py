from flask import Flask, render_template, request, redirect
import json
import time
import os

app = Flask(__name__)
SECRET_PASSWORD = "m_meliss979"

def load_fanfics():
    with open('fanfics.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_fanfics(fanfics):
    with open('fanfics.json', 'w', encoding='utf-8') as f:
        json.dump(fanfics, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    fanfics = load_fanfics()
    return render_template('index.html', fanfics=fanfics)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/fanfic/<int:fanfic_id>')
def fanfic_detail(fanfic_id):
    fanfics = load_fanfics()
    selected = next((f for f in fanfics if f['id'] == fanfic_id), None)
    if selected:
        return render_template('fanfic_detail.html', fanfic=selected)
    return "<h2>Fanfic not found</h2>", 404

@app.route('/add', methods=['GET', 'POST'])
def add_fanfic():
    if request.method == 'POST':
        if request.form.get('password') != SECRET_PASSWORD:
            return "<h2>Access Denied: Incorrect password 😞</h2>", 403

        new_fanfic = {
            "id": int(time.time()),
            "title": request.form['title'],
            "author": request.form['author'],
            "description": request.form['description'],
            "content": request.form['content'],
            "category": request.form.get('category', 'Uncategorized'),
            "likes": 0,
            "liked_by": [],  # NEW FIELD
            "comments": [],
            "image": request.form.get('image', '') or ""
        }
        fanfics = load_fanfics()
        fanfics.append(new_fanfic)
        save_fanfics(fanfics)
        return redirect('/')
    return render_template('add_fanfic.html')

# ✅ LIKE faqat bir marta bosiladigan holga o‘zgartirildi
@app.route('/like/<int:fanfic_id>', methods=['POST'])
def like_fanfic(fanfic_id):
    fanfics = load_fanfics()
    user_ip = request.remote_addr

    for f in fanfics:
        if f['id'] == fanfic_id:
            if 'liked_by' not in f:
                f['liked_by'] = []

            if user_ip not in f['liked_by']:
                f['likes'] += 1
                f['liked_by'].append(user_ip)
                save_fanfics(fanfics)
                return "Liked"
            else:
                return "Already liked"
    return "Fanfic not found", 404

@app.route('/comment/<int:fanfic_id>', methods=['POST'])
def comment_fanfic(fanfic_id):
    comment = request.form.get('comment')
    if not comment:
        return "<h2>No comment provided</h2>", 400

    fanfics = load_fanfics()
    for f in fanfics:
        if f['id'] == fanfic_id:
            f['comments'].append(comment)
            break
    save_fanfics(fanfics)
    return redirect(f'/fanfic/{fanfic_id}')

@app.route('/delete/<int:fanfic_id>', methods=['POST'])
def delete_fanfic(fanfic_id):
    password = request.form.get('password')
    if password != SECRET_PASSWORD:
        return "<h2>Access Denied: Incorrect password</h2>", 403

    fanfics = load_fanfics()
    fanfics = [f for f in fanfics if f['id'] != fanfic_id]
    save_fanfics(fanfics)
    return redirect('/')

@app.route('/edit/<int:fanfic_id>', methods=['GET', 'POST'])
def edit_fanfic(fanfic_id):
    fanfics = load_fanfics()
    selected_fanfic = next((f for f in fanfics if f['id'] == fanfic_id), None)

    if not selected_fanfic:
        return "<h2>Fanfic not found</h2>", 404

    if request.method == 'POST':
        if request.form.get('password') != SECRET_PASSWORD:
            return "<h2>Access Denied: Incorrect password</h2>", 403

        selected_fanfic['title'] = request.form['title']
        selected_fanfic['author'] = request.form['author']
        selected_fanfic['description'] = request.form['description']
        selected_fanfic['content'] = request.form['content']
        selected_fanfic['category'] = request.form.get('category', 'Uncategorized')
        selected_fanfic['image'] = request.form.get('image', '') or ""
        save_fanfics(fanfics)
        return redirect(f'/fanfic/{fanfic_id}')

    return render_template('edit_fanfic.html', fanfic=selected_fanfic)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != SECRET_PASSWORD:
            return render_template('admin_login.html', error="Incorrect password!")
        fanfics = load_fanfics()
        return render_template('admin.html', fanfics=fanfics)

    return render_template('admin_login.html')

# 🔁 Render uchun port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)