# Math Agent - AI-Powered Math Problem Generation System

A Django-based web application that generates, validates, and manages mathematical problems using multiple AI models through a configurable pipeline system.

## 🎯 Overview

Math Agent is an intelligent system that creates challenging mathematical problems across various subjects and topics. It uses a multi-stage pipeline with different AI models to:

1. **Generate** mathematical problems
2. **Create** step-by-step hints
3. **Validate** problem quality and hint accuracy
4. **Test** problems against target models
5. **Judge** solution correctness

## 🏗️ Architecture

### Pipeline Components

The system consists of five main components, each configurable with different AI providers and models:

1. **Generator**: Creates mathematical problems with solutions
2. **Hinter**: Generates progressive hints to guide students
3. **Checker**: Validates problem quality and hint accuracy
4. **Target**: Attempts to solve the generated problems
5. **Judge**: Evaluates if the target's solution is correct

### Supported AI Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo, O1, O3-mini
- **Google**: Gemini 2.5 Pro, Gemini 1.5 Pro

## 🚀 Features

### Core Functionality
- **Batch Generation**: Generate multiple problems in a single batch
- **Taxonomy Support**: Organize problems by subject and topic
- **Quality Control**: Multi-stage validation pipeline
- **Flexible Configuration**: Choose different models for each pipeline component
- **Problem Management**: View, filter, and analyze generated problems

### User Interface
- **Modern Web Interface**: Bootstrap-based responsive design
- **Real-time Generation**: Live progress tracking with loading indicators
- **Problem Details**: Comprehensive view of each generated problem
- **Batch Management**: Organize and track problem batches
- **Status Filtering**: Filter problems by validation status

### Data Management
- **Problem Storage**: Complete problem data with hints and metadata
- **Batch Organization**: Group problems by generation parameters
- **Pipeline Configuration**: Store and track model configurations
- **Status Tracking**: Track problem validation and solution status

## 📋 Prerequisites

- Python 3.8+
- Django 5.2+
- OpenAI API key
- Google API key (for Gemini models)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd math_agent_development
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
DEEPSEEK_KEY=your_deepseek_key_here  # Optional
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Application
```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
math_agent_development/
├── math_agent/                    # Main Django app
│   ├── models.py                  # Database models
│   ├── views.py                   # View logic
│   ├── urls.py                    # URL routing
│   ├── utils/                     # Pipeline utilities
│   │   ├── generator.py           # Problem generation
│   │   ├── hinter.py              # Hint generation
│   │   ├── checker.py             # Problem validation
│   │   ├── target.py              # Solution testing
│   │   ├── judge.py               # Solution evaluation
│   │   ├── call_llm_clients.py    # AI model interface
│   │   └── system_messages.py     # AI prompts
│   ├── static/                    # Static files
│   │   └── math_agent/
│   │       └── models.json        # Model configuration
│   └── templates/                 # HTML templates
│       └── math_agent/
│           ├── base.html          # Base template
│           ├── generate.html      # Problem generation form
│           ├── batches.html       # Batch list view
│           ├── problems.html      # Problem list view
│           └── problem_detail.html # Problem detail view
├── math_agent_development/        # Django project settings
├── templates/                     # Global templates
├── manage.py                      # Django management
└── requirements.txt               # Python dependencies
```

## 🔧 Configuration

### Model Configuration

The system uses a JSON configuration file (`static/math_agent/models.json`) to define available models:

```json
{
    "openai": [
        "o3-mini",
        "o1",
        "gpt-4",
        "gpt-3.5-turbo"
    ],
    "google": [
        "gemini-2.5-pro-preview-06-05",
        "gemini-1.5-pro"
    ]
}
```

### Pipeline Configuration

Each pipeline component can be configured with:
- **Provider**: AI service provider (OpenAI, Google)
- **Model**: Specific model from the provider

Default configurations:
- **Generator**: Gemini 2.5 Pro
- **Hinter**: Gemini 2.5 Pro
- **Checker**: O3 Mini
- **Target**: O1
- **Judge**: O3 Mini

## 📊 Usage

### 1. Generate Problems

1. Navigate to the "Generate" page
2. Set the number of valid problems needed
3. Upload a taxonomy JSON file
4. (Optional) Configure pipeline models
5. Click "Generate Problems"

### 2. Taxonomy Format

Create a JSON file with subject and topic structure:

```json
{
    "Linear Algebra": [
        "Eigenvalues and Eigenvectors",
        "Matrix Operations",
        "Vector Spaces"
    ],
    "Calculus": [
        "Integration",
        "Differentiation",
        "Series and Sequences"
    ]
}
```

### 3. View Results

- **Batches**: View all generated batches with statistics
- **Problems**: Browse problems by batch with filtering
- **Problem Details**: View complete problem information

## 🔍 Problem Status Types

- **Valid**: Problem passed all validation checks
- **Solved**: Target model correctly solved the problem
- **Discarded**: Problem failed validation checks

## 🎨 Customization

### Adding New Models

1. Update `static/math_agent/models.json`
2. Add provider handling in `call_llm_clients.py`
3. Update system messages if needed

### Modifying Prompts

Edit `system_messages.py` to customize AI behavior:
- `GENERATOR_MESSAGE`: Problem generation instructions
- `HINT_ONLY_MESSAGE`: Hint generation guidelines
- `CHECKER_MESSAGE`: Validation criteria
- `TARGET_MESSAGE`: Solution attempt instructions
- `JUDGE_MESSAGE`: Evaluation criteria

### Styling

The application uses Bootstrap 5. Customize styles by modifying:
- Base template (`templates/math_agent/base.html`)
- Individual page templates
- Custom CSS in template files

## 🧪 Testing

### Manual Testing
1. Generate a small batch (1-2 problems)
2. Verify problem quality and hints
3. Check target model performance
4. Review validation results

### Quality Assurance
- Monitor rejection rates
- Analyze problem difficulty distribution
- Review hint effectiveness
- Track target model success rates

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Validate all user inputs
- Implement proper authentication for production
- Monitor API usage and costs

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set production API keys
2. **Database**: Use PostgreSQL or MySQL
3. **Static Files**: Configure static file serving
4. **Web Server**: Use Gunicorn with Nginx
5. **Security**: Enable HTTPS and security headers


```

## 📈 Monitoring and Analytics

### Key Metrics
- Problem generation success rate
- Validation failure reasons
- Target model performance
- API usage and costs
- User engagement patterns

### Logging
- Generation attempts and results
- API call responses
- Error tracking
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Contact the development team


## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google AI Documentation](https://ai.google.dev/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

---

**Math Agent** - Empowering mathematical education through intelligent problem generation. 