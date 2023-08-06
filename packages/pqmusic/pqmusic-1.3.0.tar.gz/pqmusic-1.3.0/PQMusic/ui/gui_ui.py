/********************************************************************************
** Form generated from reading UI file 'gui.ui'
**
** Created by: Qt User Interface Compiler version 5.15.9
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef GUI_UI_H
#define GUI_UI_H

#include <QtCore/QLocale>
#include <QtCore/QVariant>
#include <QtGui/QIcon>
#include <QtWidgets/QApplication>
#include <QtWidgets/QFrame>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QListView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSlider>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QToolButton>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QGridLayout *gridLayout;
    QFrame *playListFrame;
    QGridLayout *gridLayout_2;
    QVBoxLayout *verticalLayout;
    QListView *playlistView;
    QHBoxLayout *playlistBtnLayout;
    QPushButton *listAddButton;
    QPushButton *listRemoveButton;
    QPushButton *listClearButton;
    QPushButton *savePlButton;
    QSpacerItem *horizontalSpacer_2;
    QHBoxLayout *optionsLayout;
    QPushButton *playlistButton;
    QPushButton *repeatButton;
    QPushButton *suffleButton;
    QToolButton *menuButton;
    QLabel *iconVol;
    QSlider *volumeSlider;
    QSpacerItem *horizontalSpacer;
    QLabel *labelCover;
    QHBoxLayout *playerLayout;
    QPushButton *queuePrevButton;
    QPushButton *playButton;
    QPushButton *queueNextButton;
    QWidget *infoWidget;
    QVBoxLayout *verticalLayout_2;
    QLabel *titleLabel;
    QLabel *artistLabel;
    QLabel *albumLabel;
    QHBoxLayout *timeLayout;
    QLabel *timeLabel;
    QSlider *timeSlider;
    QLabel *totalTimeLabel;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(435, 420);
        MainWindow->setMinimumSize(QSize(435, 0));
        MainWindow->setWindowTitle(QString::fromUtf8("PQMusic"));
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/icon.svg"), QSize(), QIcon::Normal, QIcon::Off);
        MainWindow->setWindowIcon(icon);
#if QT_CONFIG(whatsthis)
        MainWindow->setWhatsThis(QString::fromUtf8(""));
#endif // QT_CONFIG(whatsthis)
        MainWindow->setStyleSheet(QString::fromUtf8(""));
        MainWindow->setLocale(QLocale(QLocale::English, QLocale::UnitedStates));
        MainWindow->setToolButtonStyle(Qt::ToolButtonFollowStyle);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
        gridLayout = new QGridLayout(centralwidget);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        playListFrame = new QFrame(centralwidget);
        playListFrame->setObjectName(QString::fromUtf8("playListFrame"));
        playListFrame->setFrameShape(QFrame::StyledPanel);
        playListFrame->setFrameShadow(QFrame::Raised);
        gridLayout_2 = new QGridLayout(playListFrame);
        gridLayout_2->setSpacing(0);
        gridLayout_2->setObjectName(QString::fromUtf8("gridLayout_2"));
        gridLayout_2->setContentsMargins(0, 0, 0, 0);
        verticalLayout = new QVBoxLayout();
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        playlistView = new QListView(playListFrame);
        playlistView->setObjectName(QString::fromUtf8("playlistView"));
        playlistView->setEditTriggers(QAbstractItemView::NoEditTriggers);
        playlistView->setSelectionMode(QAbstractItemView::MultiSelection);

        verticalLayout->addWidget(playlistView);


        gridLayout_2->addLayout(verticalLayout, 0, 0, 1, 1);

        playlistBtnLayout = new QHBoxLayout();
        playlistBtnLayout->setObjectName(QString::fromUtf8("playlistBtnLayout"));
        listAddButton = new QPushButton(playListFrame);
        listAddButton->setObjectName(QString::fromUtf8("listAddButton"));
        QIcon icon1;
        QString iconThemeName = QString::fromUtf8("list-add");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon1 = QIcon::fromTheme(iconThemeName);
        } else {
            icon1.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        listAddButton->setIcon(icon1);
        listAddButton->setFlat(true);

        playlistBtnLayout->addWidget(listAddButton);

        listRemoveButton = new QPushButton(playListFrame);
        listRemoveButton->setObjectName(QString::fromUtf8("listRemoveButton"));
        QIcon icon2;
        iconThemeName = QString::fromUtf8("list-remove");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon2 = QIcon::fromTheme(iconThemeName);
        } else {
            icon2.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        listRemoveButton->setIcon(icon2);
        listRemoveButton->setFlat(true);

        playlistBtnLayout->addWidget(listRemoveButton);

        listClearButton = new QPushButton(playListFrame);
        listClearButton->setObjectName(QString::fromUtf8("listClearButton"));
        QIcon icon3;
        iconThemeName = QString::fromUtf8("edit-clear-all");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon3 = QIcon::fromTheme(iconThemeName);
        } else {
            icon3.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        listClearButton->setIcon(icon3);
        listClearButton->setFlat(true);

        playlistBtnLayout->addWidget(listClearButton);

        savePlButton = new QPushButton(playListFrame);
        savePlButton->setObjectName(QString::fromUtf8("savePlButton"));
        QIcon icon4;
        iconThemeName = QString::fromUtf8("document-export");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon4 = QIcon::fromTheme(iconThemeName);
        } else {
            icon4.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        savePlButton->setIcon(icon4);
        savePlButton->setFlat(true);

        playlistBtnLayout->addWidget(savePlButton);

        horizontalSpacer_2 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        playlistBtnLayout->addItem(horizontalSpacer_2);


        gridLayout_2->addLayout(playlistBtnLayout, 1, 0, 1, 1);

        gridLayout_2->setRowStretch(0, 1);

        gridLayout->addWidget(playListFrame, 3, 0, 1, 2);

        optionsLayout = new QHBoxLayout();
        optionsLayout->setObjectName(QString::fromUtf8("optionsLayout"));
        playlistButton = new QPushButton(centralwidget);
        playlistButton->setObjectName(QString::fromUtf8("playlistButton"));
        QIcon icon5;
        iconThemeName = QString::fromUtf8("view-media-playlist");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon5 = QIcon::fromTheme(iconThemeName);
        } else {
            icon5.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        playlistButton->setIcon(icon5);
        playlistButton->setCheckable(true);
        playlistButton->setChecked(false);
        playlistButton->setFlat(true);

        optionsLayout->addWidget(playlistButton);

        repeatButton = new QPushButton(centralwidget);
        repeatButton->setObjectName(QString::fromUtf8("repeatButton"));
        repeatButton->setEnabled(false);
        QIcon icon6;
        iconThemeName = QString::fromUtf8("media-playlist-repeat");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon6 = QIcon::fromTheme(iconThemeName);
        } else {
            icon6.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        repeatButton->setIcon(icon6);
        repeatButton->setCheckable(true);
        repeatButton->setFlat(true);

        optionsLayout->addWidget(repeatButton);

        suffleButton = new QPushButton(centralwidget);
        suffleButton->setObjectName(QString::fromUtf8("suffleButton"));
        suffleButton->setEnabled(false);
        QIcon icon7;
        iconThemeName = QString::fromUtf8("media-playlist-shuffle");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon7 = QIcon::fromTheme(iconThemeName);
        } else {
            icon7.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        suffleButton->setIcon(icon7);
        suffleButton->setCheckable(true);
        suffleButton->setFlat(true);

        optionsLayout->addWidget(suffleButton);

        menuButton = new QToolButton(centralwidget);
        menuButton->setObjectName(QString::fromUtf8("menuButton"));
        QIcon icon8;
        iconThemeName = QString::fromUtf8("application-menu");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon8 = QIcon::fromTheme(iconThemeName);
        } else {
            icon8.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        menuButton->setIcon(icon8);
        menuButton->setPopupMode(QToolButton::MenuButtonPopup);
        menuButton->setAutoRaise(true);
        menuButton->setArrowType(Qt::NoArrow);

        optionsLayout->addWidget(menuButton);

        iconVol = new QLabel(centralwidget);
        iconVol->setObjectName(QString::fromUtf8("iconVol"));

        optionsLayout->addWidget(iconVol);

        volumeSlider = new QSlider(centralwidget);
        volumeSlider->setObjectName(QString::fromUtf8("volumeSlider"));
        volumeSlider->setMinimumSize(QSize(80, 0));
        volumeSlider->setMaximumSize(QSize(80, 16777215));
        volumeSlider->setOrientation(Qt::Horizontal);

        optionsLayout->addWidget(volumeSlider);

        horizontalSpacer = new QSpacerItem(0, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        optionsLayout->addItem(horizontalSpacer);


        gridLayout->addLayout(optionsLayout, 2, 1, 1, 1);

        labelCover = new QLabel(centralwidget);
        labelCover->setObjectName(QString::fromUtf8("labelCover"));
        labelCover->setMinimumSize(QSize(0, 128));
        labelCover->setMaximumSize(QSize(128, 128));
        labelCover->setText(QString::fromUtf8(""));
        labelCover->setPixmap(QPixmap(QString::fromUtf8(":/icon.svg")));
        labelCover->setScaledContents(true);
        labelCover->setAlignment(Qt::AlignCenter);

        gridLayout->addWidget(labelCover, 0, 0, 1, 1);

        playerLayout = new QHBoxLayout();
        playerLayout->setObjectName(QString::fromUtf8("playerLayout"));
        queuePrevButton = new QPushButton(centralwidget);
        queuePrevButton->setObjectName(QString::fromUtf8("queuePrevButton"));
        queuePrevButton->setEnabled(false);
        QIcon icon9;
        iconThemeName = QString::fromUtf8("media-skip-backward");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon9 = QIcon::fromTheme(iconThemeName);
        } else {
            icon9.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        queuePrevButton->setIcon(icon9);
        queuePrevButton->setIconSize(QSize(22, 16));
        queuePrevButton->setAutoDefault(false);
        queuePrevButton->setFlat(true);

        playerLayout->addWidget(queuePrevButton);

        playButton = new QPushButton(centralwidget);
        playButton->setObjectName(QString::fromUtf8("playButton"));
        playButton->setEnabled(false);
        playButton->setMinimumSize(QSize(0, 0));
        playButton->setBaseSize(QSize(0, 0));
        playButton->setStyleSheet(QString::fromUtf8(""));
        QIcon icon10;
        iconThemeName = QString::fromUtf8("media-playback-start");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon10 = QIcon::fromTheme(iconThemeName);
        } else {
            icon10.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        playButton->setIcon(icon10);
        playButton->setIconSize(QSize(32, 32));
        playButton->setFlat(true);

        playerLayout->addWidget(playButton);

        queueNextButton = new QPushButton(centralwidget);
        queueNextButton->setObjectName(QString::fromUtf8("queueNextButton"));
        queueNextButton->setEnabled(false);
        QIcon icon11;
        iconThemeName = QString::fromUtf8("media-skip-forward");
        if (QIcon::hasThemeIcon(iconThemeName)) {
            icon11 = QIcon::fromTheme(iconThemeName);
        } else {
            icon11.addFile(QString::fromUtf8("."), QSize(), QIcon::Normal, QIcon::Off);
        }
        queueNextButton->setIcon(icon11);
        queueNextButton->setFlat(true);

        playerLayout->addWidget(queueNextButton);


        gridLayout->addLayout(playerLayout, 2, 0, 1, 1);

        infoWidget = new QWidget(centralwidget);
        infoWidget->setObjectName(QString::fromUtf8("infoWidget"));
        infoWidget->setMaximumSize(QSize(340, 16777215));
        verticalLayout_2 = new QVBoxLayout(infoWidget);
        verticalLayout_2->setSpacing(0);
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        verticalLayout_2->setContentsMargins(0, 0, 0, 0);
        titleLabel = new QLabel(infoWidget);
        titleLabel->setObjectName(QString::fromUtf8("titleLabel"));
        titleLabel->setWordWrap(true);

        verticalLayout_2->addWidget(titleLabel);

        artistLabel = new QLabel(infoWidget);
        artistLabel->setObjectName(QString::fromUtf8("artistLabel"));

        verticalLayout_2->addWidget(artistLabel);

        albumLabel = new QLabel(infoWidget);
        albumLabel->setObjectName(QString::fromUtf8("albumLabel"));

        verticalLayout_2->addWidget(albumLabel);

        timeLayout = new QHBoxLayout();
        timeLayout->setSpacing(2);
        timeLayout->setObjectName(QString::fromUtf8("timeLayout"));
        timeLayout->setContentsMargins(0, -1, 0, -1);
        timeLabel = new QLabel(infoWidget);
        timeLabel->setObjectName(QString::fromUtf8("timeLabel"));
        timeLabel->setMinimumSize(QSize(0, 0));
        timeLabel->setMaximumSize(QSize(16777215, 16777215));
        timeLabel->setSizeIncrement(QSize(50, 0));
        timeLabel->setBaseSize(QSize(0, 0));
        timeLabel->setStyleSheet(QString::fromUtf8("QLabel {\n"
"	width: 200px\n"
"}"));
        timeLabel->setText(QString::fromUtf8("0:00:00"));

        timeLayout->addWidget(timeLabel);

        timeSlider = new QSlider(infoWidget);
        timeSlider->setObjectName(QString::fromUtf8("timeSlider"));
        timeSlider->setOrientation(Qt::Horizontal);

        timeLayout->addWidget(timeSlider);

        totalTimeLabel = new QLabel(infoWidget);
        totalTimeLabel->setObjectName(QString::fromUtf8("totalTimeLabel"));
        totalTimeLabel->setText(QString::fromUtf8("0:00:00"));
        totalTimeLabel->setAlignment(Qt::AlignCenter);

        timeLayout->addWidget(totalTimeLabel);


        verticalLayout_2->addLayout(timeLayout);


        gridLayout->addWidget(infoWidget, 0, 1, 1, 1);

        gridLayout->setRowStretch(3, 1);
        MainWindow->setCentralWidget(centralwidget);

        retranslateUi(MainWindow);

        queuePrevButton->setDefault(false);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        listAddButton->setText(QString());
        listRemoveButton->setText(QString());
        listClearButton->setText(QString());
        savePlButton->setText(QString());
        playlistButton->setText(QString());
        repeatButton->setText(QString());
        suffleButton->setText(QString());
        menuButton->setText(QString());
        iconVol->setText(QString());
        queuePrevButton->setText(QString());
        playButton->setText(QString());
        queueNextButton->setText(QString());
        titleLabel->setText(QCoreApplication::translate("MainWindow", "Track Title", nullptr));
        artistLabel->setText(QCoreApplication::translate("MainWindow", "Artist", nullptr));
        albumLabel->setText(QCoreApplication::translate("MainWindow", "Album", nullptr));
        (void)MainWindow;
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // GUI_UI_H
