// =====================
// JOKE TOAST SYSTEM
// =====================

let lastEmotion = null;
let jokeToastTimer = null;
const TOAST_DURATION = 12000;
const SAD_EMOTIONS = ['sad'];

function showJokeToast(jokeText) {
    const toast = document.getElementById('joke-toast');
    const toastBody = document.getElementById('joke-toast-text');
    if (!toast || !toastBody) return;

    toastBody.innerText = jokeText;
    toast.classList.add('show');

    if (jokeToastTimer) clearTimeout(jokeToastTimer);
    jokeToastTimer = setTimeout(() => closeJokeToast(), TOAST_DURATION);
}

function closeJokeToast() {
    const toast = document.getElementById('joke-toast');
    if (toast) toast.classList.remove('show');
    if (jokeToastTimer) { clearTimeout(jokeToastTimer); jokeToastTimer = null; }
}

function triggerJokeForEmotion(emotion) {
    if (!SAD_EMOTIONS.includes(emotion)) return;
    fetch('/get_joke')
        .then(r => r.json())
        .then(j => { if (j.joke) showJokeToast(j.joke); })
        .catch(console.error);
}

// =====================
// MUSIC CARD SYSTEM
// =====================

let musicCardTimer = null;
const MUSIC_DURATION = 20000; // 20s before auto-hide

const MOOD_LABELS = {
    happy: '😊 Songs for a Happy Mood',
    sad: '😢 Songs to Heal Your Heart',
    angry: '😠 Songs for Your Energy',
    relaxed: '😎 Songs to Keep You Relaxed',
    stressed: '🤯 Songs to Ease the Stress',
    neutral: '😌 Songs for Now',
    fear: '😨 Songs for the Moment',
    disgust: '🤢 Songs to Shift Your Mood',
};

function showMusicCard(emotion, songs) {
    const card = document.getElementById('music-card');
    const title = document.getElementById('music-card-title');
    const list = document.getElementById('music-song-list');
    if (!card || !list) return;

    title.innerText = MOOD_LABELS[emotion] || '🎵 Songs for your mood';
    list.innerHTML = songs.map((s, i) => {
        const query = encodeURIComponent(`${s.artist} ${s.title}`);
        const ytUrl = `https://www.youtube.com/results?search_query=${query}`;
        return `
        <li class="music-song-item" onclick="window.open('${ytUrl}','_blank')" style="cursor:pointer;" title="Search on YouTube">
            <span class="song-num">${i + 1}</span>
            <div class="song-info">
                <div class="song-title">${s.title}</div>
                <div class="song-artist">${s.artist}</div>
            </div>
            <span class="song-year">${s.year}&nbsp;▶</span>
        </li>`;
    }).join('');

    card.classList.add('show');

    if (musicCardTimer) clearTimeout(musicCardTimer);
    musicCardTimer = setTimeout(() => closeMusicCard(), MUSIC_DURATION);
}

function closeMusicCard() {
    const card = document.getElementById('music-card');
    if (card) card.classList.remove('show');
    if (musicCardTimer) { clearTimeout(musicCardTimer); musicCardTimer = null; }
}

function fetchMusicForEmotion(emotion) {
    fetch(`/get_music?emotion=${encodeURIComponent(emotion)}`)
        .then(r => r.json())
        .then(data => {
            if (data.songs && data.songs.length) {
                showMusicCard(emotion, data.songs);
            }
        })
        .catch(console.error);
}

// =====================
// DETECTION POLLING
// =====================

document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const overlay = document.getElementById('detection-overlay');
    const videoFeed = document.getElementById('video-feed');

    if (!startBtn) return;

    let statsInterval;

    startBtn.addEventListener('click', (e) => {
        e.preventDefault();
        overlay.classList.remove('hidden');
        videoFeed.style.display = 'block';
        videoFeed.src = "/video_feed";
        statsInterval = setInterval(fetchStats, 1500);
    });

    stopBtn.addEventListener('click', () => {
        overlay.classList.add('hidden');
        videoFeed.src = "";
        videoFeed.style.display = 'none';
        if (statsInterval) clearInterval(statsInterval);
        closeJokeToast();
        closeMusicCard();
        lastEmotion = null;
    });
});

function fetchStats() {
    fetch('/emotion_status')
        .then(res => res.json())
        .then(data => {
            const dominantEl = document.getElementById('dominant-mood');
            const emojiEl = document.getElementById('mood-emoji');
            const benefitsContainer = document.getElementById('benefits-container');
            const quickResetText = document.getElementById('quick-reset-text');
            const jokeSection = document.getElementById('joke-section');
            if (jokeSection) jokeSection.classList.add('hidden');

            if (data.dominant_emotion) {
                const userName = data.user_name || "Friend";
                dominantEl.innerText = `${userName}, you seem ${data.dominant_emotion}`;

                const emojiMap = {
                    'happy': '😊',
                    'sad': '😢',
                    'angry': '😠',
                    'relaxed': '😎',
                    'stressed': '🤯',
                    'neutral': '😌',
                    'surprise': '😲',
                    'fear': '😨',
                    'disgust': '🤢'
                };
                const emoKey = data.dominant_emotion.toLowerCase();
                emojiEl.innerText = emojiMap[emoKey] || '✨';

                if (data.quick_reset) {
                    benefitsContainer.classList.remove('hidden');
                    quickResetText.innerText = data.quick_reset;
                } else {
                    benefitsContainer.classList.add('hidden');
                }

                // Trigger on emotion CHANGE only
                if (emoKey !== lastEmotion) {
                    lastEmotion = emoKey;

                    // Joke toast — only for Sad
                    if (SAD_EMOTIONS.includes(emoKey)) {
                        triggerJokeForEmotion(emoKey);
                    } else {
                        closeJokeToast();
                    }

                    // Music card — for every emotion change
                    fetchMusicForEmotion(emoKey);
                }
            }
        })
        .catch(console.error);
}

// =====================
// PROFILE DROPDOWN
// =====================
function toggleProfile() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('hidden');

    document.addEventListener('click', function closeMenu(e) {
        if (!e.target.closest('.profile-container')) {
            dropdown.classList.add('hidden');
            document.removeEventListener('click', closeMenu);
        }
    });
}
