from scraping_system.scraper import scrape


def main():
    url = input("Enter article URL: ").strip()

    article = scrape(url)

    print("\nTITLE")
    print(article.title)

    print("\nPARAGRAPHS")
    print(f"Total: {len(article.paragraphs)}")

    for paragraph in article.paragraphs[:5]:
        print(f"\n[{paragraph.id}]")
        print(paragraph.text)

    print("\nIMAGES")
    print(f"Total: {len(article.images)}")

    for image in article.images[:5]:
        print(f"\n[{image.id}]")
        print(image.url)
        print("Alt:", image.alt)


if __name__ == "__main__":
    main()
