const startPage = document.querySelector('.start-page');
const thoughtPage = document.querySelector('.thought-page');

const startButton = document.getElementById('start-btn');
const thoughtButton = document.getElementById('thought-btn');

const thoughtText = document.getElementById('thought-text');
const thoughtAuthor = document.getElementById('author-name');

// фейк данные (будет запрос к api)
const thoughtArr = [
    {
        id: 1,
        text: 'Оставим мертвым хоронить мертвых, а пока жив, надо жить и быть счастливым',
        author: 'Лев Толстой',
        is_public: true
    },
    {
        id: 2,
        text: 'Стремитесь не к успеху, а к ценностям, которые он дает',
        author: 'Альберт Эйнштейн',
        is_public: true
    },
    {
        id: 3,
        text: 'Нет ничего более сильного, чем человек, решивший встать после падения',
        author: 'Фёдор Достоевский',
        is_public: true
    },
];

function choseNumber() {
    return Math.floor(thoughtArr.length * Math.random());
}
// фейк данные (будет запрос к api)

startButton.addEventListener('click', () => {
    startPage.hidden = !startPage.hidden
    thoughtPage.hidden = !thoughtPage.hidden

    thought = thoughtArr[choseNumber()]

    thoughtText.textContent = '"' + thought.text + '"';
    thoughtAuthor.textContent = '- ' + thought.author;
});

thoughtButton.addEventListener('click', () => {
    thought = thoughtArr[choseNumber()]

    thoughtText.textContent = '"' + thought.text + '"';
    thoughtAuthor.textContent = '- ' + thought.author;
})