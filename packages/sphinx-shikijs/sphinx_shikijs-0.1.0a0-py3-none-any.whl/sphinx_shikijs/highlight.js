(() => {
  const getHighlightLang = (el) => {
    return Array.from(el.classList)
      .filter((cls) => cls.startsWith("language-"))[0]
      ?.split("-")[1];
  };

  // const highlight = (el) => {
  //   shiki
  //     .getHighlighter({
  //       theme: highlightTheme,
  //     })
  //     .then((highlighter) => {
  //       const lang = getHighlightLang(el);
  //       console.log(lang);
  //       const code = highlighter.codeToHtml(el.textContent, {
  //         lang: lang,
  //       });
  //       el.innerHTML = code;
  //     });
  // };
  document.addEventListener("DOMContentLoaded", async () => {
    const langs = [];
    document.querySelectorAll(".highlight").forEach((el) => {
      langs.push(getHighlightLang(el));
    });
    console.log(langs);

    const highlighter = await shiki.getHighlighter({
      theme: highlightTheme,
      langs: langs,
    });

    document.querySelectorAll(".highlight").forEach((el) => {
      const lang = getHighlightLang(el);
      console.log(lang);
      const code = highlighter.codeToHtml(el.textContent, {
        lang: lang,
      });
      el.innerHTML = code;
    });
  });
})();
