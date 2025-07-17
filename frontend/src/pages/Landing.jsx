import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Landing.css';

const Landing = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const goToLogin = () => {
    navigate('/login');
  };

  const openGitHub = () => {
    window.open('https://github.com/Adolfo2231/billax', '_blank');
  };

  return (
    <div className="landing-page">
      {/* Header Navigation */}
      <header className={`header ${isScrolled ? 'scrolled' : ''}`}>
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">💼</span>
            <span className="logo-text">Billax</span>
          </div>
          <nav className="nav-menu">
            <button onClick={() => scrollToSection('features')} className="nav-link">
              Features
            </button>
            <button onClick={() => scrollToSection('about')} className="nav-link">
              About
            </button>
            <button onClick={goToLogin} className="cta-button">
              Try Billax
            </button>
          </nav>
        </div>
      </header>

      {/* Intro Section */}
      <section id="intro" className="intro-section">
        <div className="intro-background">
          <div className="floating-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
          </div>
        </div>
        <div className="intro-content">
          <div className="intro-text">
            <div className="badge">
              <span>🚀</span> AI-Powered Financial Management
            </div>
            <h1 className="intro-title">
              Take Control of Your <span className="highlight">Financial Future</span>
            </h1>
            <p className="intro-description">
              Billax is your intelligent personal finance assistant that helps you understand, 
              organize, and project your finances with AI-powered insights and real-time bank integration.
            </p>
            <div className="intro-stats">
              <div className="stat-badge">
                <span className="stat-number">500+</span>
                <span className="stat-label">Users</span>
              </div>
              <div className="stat-badge">
                <span className="stat-number">$2M+</span>
                <span className="stat-label">Tracked</span>
              </div>
              <div className="stat-badge">
                <span className="stat-number">24/7</span>
                <span className="stat-label">AI Support</span>
              </div>
            </div>
            <div className="intro-buttons">
              <button onClick={goToLogin} className="primary-button">
                <span className="button-icon">💼</span>
                Start Managing Your Money
                <span className="button-arrow">→</span>
              </button>
              <button onClick={() => scrollToSection('features')} className="secondary-button">
                <span className="button-icon">📊</span>
                See How It Works
              </button>
            </div>
          </div>
          <div className="intro-image">
            <div className="hero-mockup">
              <div className="mockup-screen">
                <div className="mockup-header">
                  <div className="mockup-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div className="mockup-content">
                  <div className="mockup-chart">
                    <div className="chart-line"></div>
                    <div className="chart-points">
                      <div className="point point-1"></div>
                      <div className="point point-2"></div>
                      <div className="point point-3"></div>
                      <div className="point point-4"></div>
                    </div>
                  </div>
                  <div className="mockup-stats">
                    <div className="stat-item">
                      <span className="stat-label">Monthly Spending</span>
                      <span className="stat-value">$2,450</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Savings Goal</span>
                      <span className="stat-value">75%</span>
                    </div>
                  </div>
                  <div className="mockup-notification">
                    <div className="notification-icon">🤖</div>
                    <div className="notification-text">
                      <strong>AI Insight:</strong> You can save $200 this month!
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Powerful Features for Smart Money Management</h2>
            <p className="section-subtitle">
              Everything you need to take control of your financial life
            </p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-header">
                <div className="feature-icon">🏦</div>
                <div className="feature-badge">Secure</div>
              </div>
              <h3 className="feature-title">Bank Account Integration</h3>
              <p className="feature-description">
                Connect your bank accounts securely with Plaid integration. View real-time transactions 
                and get automatic categorization of your spending patterns.
              </p>
              <div className="feature-visual">
                <div className="feature-mockup bank-mockup">
                  <div className="mockup-accounts">
                    <div className="account-item">
                      <div className="account-icon">🏦</div>
                      <div className="account-info">
                        <span className="account-name">Chase Bank</span>
                        <span className="account-balance">$5,240.50</span>
                      </div>
                      <div className="account-status connected">Connected</div>
                    </div>
                    <div className="account-item">
                      <div className="account-icon">💳</div>
                      <div className="account-info">
                        <span className="account-name">Credit Card</span>
                        <span className="account-balance">-$1,200.00</span>
                      </div>
                      <div className="account-status connected">Connected</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-header">
                <div className="feature-icon">🤖</div>
                <div className="feature-badge">AI-Powered</div>
              </div>
              <h3 className="feature-title">AI Financial Assistant</h3>
              <p className="feature-description">
                Ask questions about your finances and get intelligent insights. Our AI assistant 
                helps you understand spending patterns and suggests ways to save money.
              </p>
              <div className="feature-visual">
                <div className="feature-mockup ai-mockup">
                  <div className="chat-bubble">
                    <div className="chat-avatar">🤖</div>
                    <div className="chat-message">
                      "You've spent 30% more on dining this month. Consider cooking at home to save $200!"
                    </div>
                  </div>
                  <div className="chat-typing">
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-header">
                <div className="feature-icon">📊</div>
                <div className="feature-badge">Smart</div>
              </div>
              <h3 className="feature-title">Smart Analytics & Goals</h3>
              <p className="feature-description">
                Track your financial goals with visual progress indicators. Get detailed analytics 
                on your spending habits and create personalized savings targets.
              </p>
              <div className="feature-visual">
                <div className="feature-mockup goals-mockup">
                  <div className="goal-progress">
                    <div className="goal-item">
                      <span className="goal-name">Vacation Fund</span>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{width: '75%'}}></div>
                      </div>
                      <span className="goal-amount">$3,750 / $5,000</span>
                    </div>
                    <div className="goal-item">
                      <span className="goal-name">Emergency Fund</span>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{width: '45%'}}></div>
                      </div>
                      <span className="goal-amount">$2,250 / $5,000</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <div className="container">
          <div className="about-content">
            <div className="about-text">
              <h2 className="section-title">About Billax</h2>
              <div className="about-story">
                <p>
                  Billax was born from a personal struggle with financial management. As someone who 
                  found it challenging to keep track of multiple bank accounts, credit cards, and 
                  financial goals, I realized there had to be a better way to manage personal finances.
                </p>
                <p>
                  The inspiration came during a particularly stressful month when I missed several 
                  bill payments and realized I had no clear picture of my financial health. I wanted 
                  to create a tool that would not only track transactions but also provide intelligent 
                  insights and help users make better financial decisions.
                </p>
                <p>
                  This project represents months of development, learning, and iteration. It's built 
                  as a Portfolio Project for Holberton School, showcasing full-stack development 
                  skills with modern technologies like React, Flask, and AI integration.
                </p>
              </div>
              
              <div className="developer-info">
                <h3>Meet the Developer</h3>
                <div className="developer-card">
                  <div className="developer-avatar">👨‍💻</div>
                  <div className="developer-details">
                    <h4>Adolfo Rodriguez</h4>
                    <p>Full Stack Developer & Software Architect</p>
                    <div className="social-links">
                      <a href="https://www.linkedin.com/in/adolfo-rodriguez-22b178330/" 
                         target="_blank" rel="noopener noreferrer" className="social-link">
                        <span>💼</span> LinkedIn
                      </a>
                      <a href="https://github.com/Adolfo2231" 
                         target="_blank" rel="noopener noreferrer" className="social-link">
                        <span>💻</span> GitHub
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div className="project-links">
                <button onClick={openGitHub} className="github-button">
                  <span>📁</span> View Source Code
                </button>
                <button onClick={goToLogin} className="demo-button">
                  <span>🚀</span> Live Demo
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-logo">
                <span className="logo-icon">💼</span>
                <span className="logo-text">Billax</span>
              </div>
              <p>Your intelligent personal finance assistant</p>
            </div>
            <div className="footer-section">
              <h4>Quick Links</h4>
              <button onClick={() => scrollToSection('features')} className="footer-link">
                Features
              </button>
              <button onClick={() => scrollToSection('about')} className="footer-link">
                About
              </button>
            </div>
            <div className="footer-section">
              <h4>Connect</h4>
              <a href="https://github.com/Adolfo2231/billax" 
                 target="_blank" rel="noopener noreferrer" className="footer-link">
                GitHub
              </a>
              <a href="https://www.linkedin.com/in/adolfo-rodriguez-22b178330/" 
                 target="_blank" rel="noopener noreferrer" className="footer-link">
                LinkedIn
              </a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 Billax. Built with ❤️ for better financial management.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing; 