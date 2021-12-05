from conventer import WayConventer
import path_finder
import webbrowser
import pathlib

if __name__ == "__main__":
    # cathegory = int(input("Введите категорию похода (1-6): "))
    path_finder = path_finder.PathFindingAlgorithm(-35, "р.D", "р.F")
    # path_finder = path_finder.PathFindingAlgorithm(5, "лед.Дзынал", "лед.Цаннер")
    print(path_finder)
    conv = WayConventer(path_finder.path)
    link = ('file:///'+str(pathlib.Path().absolute())+'/html_template/index2.html').replace(f"\\", "/")
    webbrowser.open(link)
    