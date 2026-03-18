[TOC]

# Markdown文件内部链接创建

- **File list**: 
  - [[#20241020075710@InternalLink@keyboardIdleDetectREADME]]
  - [[#20241020075710@InternalLink@keyboardIdleDetectCPP]]

---

<a id="20241020075710@InternalLink@keyboardIdleDetectREADME"></a>

- README.txt
```txt
Step 01. You can set environment variable:
    keyboardNoPressTimeOutSec

Step 02. then you can run the program, 
    the system will reboot after keyboardNoPressTimeOutSec
    (env vars: keyboardNoPressTimeOutSec, keyboardNoPressTimeStepLenSec)

Step 03. Set it to start automatically when you boot up.
    First create the shortcut, 
    then Ctrl+r, 
    then type shell:common startup, 
    and copy the shortcut to this directory.


How to build program (WinMain):
    01. Create Win32 console project
    02. linker --> system --> subsystem --> WINDOWS
    03. C/C++  --> preprocessor --> preprocessor define --> _CONSOLE --> _WINDOWS
```



# Qt新建工程

- [[#202412191732@InternalLink@Qt新建工程@mainwindow_h]]
- [[#202412191732@InternalLink@Qt新建工程@mainwindow_cpp]]

---

<a id="202412191732@InternalLink@Qt新建工程@mainwindow_h"></a>

- mainwindow.h

```cpp{.line-numbers}
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
};

#endif // MAINWINDOW_H
```

---


<a id="202412191732@InternalLink@Qt新建工程@mainwindow_cpp"></a>

- mainwindow.cpp

```cpp{.line-numbers}
#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}
```

# QCheckBox基础示例

- 示例说明: 复选框，单选，全选，多选，取消全选功能。
- [[#202412191740@InternalLink@QCheckBox基础示例@mainwindow_h]]
- [[#202412191740@InternalLink@QCheckBox基础示例@mainwindow_cpp]]


---

<a id="202412191740@InternalLink@QCheckBox基础示例@mainwindow_h"></a>

- mainwindow.h

```cpp{.line-numbers}
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QCheckBox>
#include <QLabel>
#include <QHeaderView>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private:
    QCheckBox *checkBoxAll;
    QCheckBox *checkBoxRange;
    QCheckBox *checkBox01;
    QCheckBox *checkBox02;
    QCheckBox *checkBox03;
    QCheckBox *checkBox04;
    QCheckBox *checkBox05;
    QLabel *label;

private slots:
    void checkChangeAll();
    void checkChangeRange();
    void checkChange();

signals:


private:
    Ui::MainWindow *ui;
};

#endif // MAINWINDOW_H
```

---

<a id="202412191740@InternalLink@QCheckBox基础示例@mainwindow_cpp"></a>

- mainwindow.cpp

```cpp{.line-numbers}
#include "mainwindow.h"
#include "ui_mainwindow.h"

#include "QDebug"
#include <QSysInfo>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);


    checkBoxAll = new QCheckBox(this);
    checkBoxRange = new QCheckBox(this);
    checkBox01 = new QCheckBox(this);
    checkBox02 = new QCheckBox(this);
    checkBox03 = new QCheckBox(this);
    checkBox04 = new QCheckBox(this);
    checkBox05 = new QCheckBox(this);
    label = new QLabel(this);


    //设置在界面上的坐标位置
    int ax = 10;
    int ay = 50;
    int aw = 50;
    int ah = 50;
    checkBoxAll->setGeometry((ax=ax + 0), ay, aw, ah);
    checkBoxRange->setGeometry((ax=ax + 50), ay, aw, ah);
    checkBox01->setGeometry((ax=ax + 50), ay, aw, ah);
    checkBox02->setGeometry((ax=ax + 50), ay, aw, ah);
    checkBox03->setGeometry((ax=ax + 50), ay, aw, ah);
    checkBox04->setGeometry((ax=ax + 50), ay, aw, ah);
    checkBox05->setGeometry((ax=ax + 50), ay, aw, ah);
    label->setGeometry( 10+50, 100, 200, 30);

    //设置显示的标签
    checkBoxAll->setText("全选");
    checkBoxRange->setText("多选");
    checkBox01->setText("111");
    checkBox02->setText("222");
    checkBox03->setText("333");
    checkBox04->setText("444");
    checkBox05->setText("555");

    connect(checkBoxAll, SIGNAL(clicked()), this, SLOT(checkChangeAll()));
    connect(checkBoxRange, SIGNAL(clicked()), this, SLOT(checkChangeRange()));
    connect(checkBox01, SIGNAL(stateChanged(int)), this, SLOT(checkChange()));
    connect(checkBox02, SIGNAL(stateChanged(int)), this, SLOT(checkChange()));
    connect(checkBox03, SIGNAL(stateChanged(int)), this, SLOT(checkChange()));
    connect(checkBox04, SIGNAL(stateChanged(int)), this, SLOT(checkChange()));
    connect(checkBox05, SIGNAL(stateChanged(int)), this, SLOT(checkChange()));
}

static QString labelStr;

void MainWindow::checkChangeAll()
{
    QObject *obj = sender();
    if (obj == checkBoxAll)
    {
        if (checkBoxAll->checkState() == Qt::Checked)
        {
            checkBox01->setCheckState(Qt::Checked);
            checkBox02->setCheckState(Qt::Checked);
            checkBox03->setCheckState(Qt::Checked);
            checkBox04->setCheckState(Qt::Checked);
            checkBox05->setCheckState(Qt::Checked);
        } else
        {
            checkBox01->setCheckState(Qt::Unchecked);
            checkBox02->setCheckState(Qt::Unchecked);
            checkBox03->setCheckState(Qt::Unchecked);
            checkBox04->setCheckState(Qt::Unchecked);
            checkBox05->setCheckState(Qt::Unchecked);
        }
    }
}

void MainWindow::checkChangeRange()
{
    QObject *obj = sender();
    if (obj == checkBoxRange)
    {
        if (checkBoxRange->checkState() == Qt::Checked)
        {
            QCheckBox *allBoxs[] = {
                checkBox01,
                checkBox02,
                checkBox03,
                checkBox04,
                checkBox05,
            };
            int rangeStart = -1;

            //获取范围起始索引号
            int boxCnt = sizeof(allBoxs)/sizeof(allBoxs[0]);
            for(int i=0; i<boxCnt; i++)
            {
                if (allBoxs[i]->checkState() == Qt::Checked)
                {
                    rangeStart = i+1;
                    //printf("rangeStart = %d\n", rangeStart);fflush(stdout);
                    break;
                }
            }


            //如果小于0,则表示没有区间信息
            if (rangeStart >= 0)
            {
                //从其实索引开始,之后的都设置为选中,直到遇到已选中的为止
                for(int i=rangeStart; i<boxCnt; i++)
                {
                    if (allBoxs[i]->checkState() == Qt::Checked)
                    {
                        break;
                    }

                    allBoxs[i]->setCheckState(Qt::Checked);
                }
            }

        } else
        {
        }
    }
}

void MainWindow::checkChange()
{
    QObject *obj = sender();

    if (obj == checkBox01)
    {
        if (checkBox01->checkState() == Qt::Checked)
            labelStr += "111 ";
        else
            labelStr = labelStr.replace(QString("111 "), QString(""));
    }

    if (obj == checkBox02)
    {
        if (checkBox02->checkState() == Qt::Checked)
            labelStr += "222 ";
        else
            labelStr = labelStr.replace(QString("222 "), QString(""));
    }

    if (obj == checkBox03)
    {
        if (checkBox03->checkState() == Qt::Checked)
            labelStr += "333 ";
        else
            labelStr = labelStr.replace(QString("333 "), QString(""));
    }

    if (obj == checkBox04)
    {
        if (checkBox04->checkState() == Qt::Checked)
            labelStr += "444 ";
        else
            labelStr = labelStr.replace(QString("444 "), QString(""));
    }

    if (obj == checkBox05)
    {
        if (checkBox05->checkState() == Qt::Checked)
            labelStr += "555 ";
        else
            labelStr = labelStr.replace(QString("555 "), QString(""));
    }

    label->setText(labelStr);

}



MainWindow::~MainWindow()
{
    delete ui;
}
```


# QTableView




# QVector










