module.exports = {
  plugins: [
    require('postcss-prefix-selector')({
      prefix: '.bootstrap-scope',
      transform: function (prefix, selector, prefixedSelector) {
        if (selector.startsWith('html') || selector.startsWith('body')) {
          return prefixedSelector.replace(/^\.bootstrap-scope /, '');
        }
        return prefixedSelector;
      }
    })
  ]
}
