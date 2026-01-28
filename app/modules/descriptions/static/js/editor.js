const editor = grapesjs.init({
  container : '#editor',
  fromElement: true,
  height: '500px',
  width: 'auto',
  storageManager: { type: null }, // wyłącz storage (możesz potem dodać backend)
  plugins: ['gjs-preset-webpage'],
});
