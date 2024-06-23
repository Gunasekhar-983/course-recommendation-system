from flask import Flask, render_template, request, jsonify
import pickle

app = Flask(__name__)

# Load only the data file initially
data = pickle.load(open('data.pkl', 'rb'))
similarity = None

def load_similarity():
    global similarity
    if similarity is None:
        similarity = pickle.load(open('similar.pkl', 'rb'))

def recommend(course_name):
    try:
        idx = data[data['Course Name'].str.contains(course_name, case=False, na=False)].index[0]
    except IndexError:
        return []
    
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    recommended = [{
        "name": data.iloc[i[0]]['Course Name'],
        "url": data.iloc[i[0]]['Course URL'],
        "difficulty": data.iloc[i[0]]['Difficulty Level'],
        "specialization": data.iloc[i[0]]['Specialization'],
        "is_emerging": str(data.iloc[i[0]]['Is_Emerging_Tech']).lower()
    } for i in sim_scores]
    return recommended

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_courses', methods=['GET'])
def search_courses():
    query = request.args.get('query', '').lower()
    
    # Load similarity data when user starts searching
    load_similarity()
    
    matching_courses = data[data['Course Name'].str.lower().str.contains(query)].to_dict('records')
    for course in matching_courses:
        course['Is_Emerging_Tech'] = str(course['Is_Emerging_Tech']).lower()
    return jsonify(matching_courses[:10])

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    course_name = request.form['course_name']
    recommendations = recommend(course_name)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)