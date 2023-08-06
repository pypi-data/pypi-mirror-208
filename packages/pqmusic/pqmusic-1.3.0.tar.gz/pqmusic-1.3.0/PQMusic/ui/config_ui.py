/********************************************************************************
** Form generated from reading UI file 'config.ui'
**
** Created by: Qt User Interface Compiler version 5.15.9
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef CONFIG_UI_H
#define CONFIG_UI_H

#include <QtCore/QLocale>
#include <QtCore/QVariant>
#include <QtGui/QIcon>
#include <QtWidgets/QApplication>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QDialog>
#include <QtWidgets/QDialogButtonBox>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>

QT_BEGIN_NAMESPACE

class Ui_Config_Dialog
{
public:
    QGridLayout *gridLayout;
    QLabel *label;
    QCheckBox *minimizeToTray;
    QCheckBox *cbSaveVolume;
    QLineEdit *musicFolderEdit;
    QPushButton *setMusicFolderBtn;
    QCheckBox *notifyOnChange;
    QCheckBox *cbDownCover;
    QDialogButtonBox *buttonBox;
    QCheckBox *cbSavePlaylist;

    void setupUi(QDialog *Config_Dialog)
    {
        if (Config_Dialog->objectName().isEmpty())
            Config_Dialog->setObjectName(QString::fromUtf8("Config_Dialog"));
        Config_Dialog->setWindowModality(Qt::WindowModal);
        Config_Dialog->resize(365, 316);
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/icon.svg"), QSize(), QIcon::Normal, QIcon::Off);
        Config_Dialog->setWindowIcon(icon);
#if QT_CONFIG(tooltip)
        Config_Dialog->setToolTip(QString::fromUtf8(""));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        Config_Dialog->setWhatsThis(QString::fromUtf8(""));
#endif // QT_CONFIG(whatsthis)
        Config_Dialog->setLocale(QLocale(QLocale::English, QLocale::UnitedStates));
        Config_Dialog->setModal(true);
        gridLayout = new QGridLayout(Config_Dialog);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        label = new QLabel(Config_Dialog);
        label->setObjectName(QString::fromUtf8("label"));

        gridLayout->addWidget(label, 0, 0, 1, 1);

        minimizeToTray = new QCheckBox(Config_Dialog);
        minimizeToTray->setObjectName(QString::fromUtf8("minimizeToTray"));

        gridLayout->addWidget(minimizeToTray, 3, 0, 1, 3);

        cbSaveVolume = new QCheckBox(Config_Dialog);
        cbSaveVolume->setObjectName(QString::fromUtf8("cbSaveVolume"));

        gridLayout->addWidget(cbSaveVolume, 5, 0, 1, 1);

        musicFolderEdit = new QLineEdit(Config_Dialog);
        musicFolderEdit->setObjectName(QString::fromUtf8("musicFolderEdit"));

        gridLayout->addWidget(musicFolderEdit, 1, 0, 1, 1);

        setMusicFolderBtn = new QPushButton(Config_Dialog);
        setMusicFolderBtn->setObjectName(QString::fromUtf8("setMusicFolderBtn"));

        gridLayout->addWidget(setMusicFolderBtn, 1, 1, 1, 1);

        notifyOnChange = new QCheckBox(Config_Dialog);
        notifyOnChange->setObjectName(QString::fromUtf8("notifyOnChange"));

        gridLayout->addWidget(notifyOnChange, 2, 0, 1, 3);

        cbDownCover = new QCheckBox(Config_Dialog);
        cbDownCover->setObjectName(QString::fromUtf8("cbDownCover"));

        gridLayout->addWidget(cbDownCover, 4, 0, 1, 2);

        buttonBox = new QDialogButtonBox(Config_Dialog);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);

        gridLayout->addWidget(buttonBox, 7, 0, 1, 1);

        cbSavePlaylist = new QCheckBox(Config_Dialog);
        cbSavePlaylist->setObjectName(QString::fromUtf8("cbSavePlaylist"));

        gridLayout->addWidget(cbSavePlaylist, 6, 0, 1, 2);


        retranslateUi(Config_Dialog);
        QObject::connect(buttonBox, SIGNAL(accepted()), Config_Dialog, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), Config_Dialog, SLOT(reject()));

        QMetaObject::connectSlotsByName(Config_Dialog);
    } // setupUi

    void retranslateUi(QDialog *Config_Dialog)
    {
        Config_Dialog->setWindowTitle(QCoreApplication::translate("Config_Dialog", "Config PQMusic", nullptr));
        label->setText(QCoreApplication::translate("Config_Dialog", "Default music folder:", nullptr));
        minimizeToTray->setText(QCoreApplication::translate("Config_Dialog", "Minimize to system tray when closing window", nullptr));
        cbSaveVolume->setText(QCoreApplication::translate("Config_Dialog", "Save volume on close", nullptr));
        setMusicFolderBtn->setText(QCoreApplication::translate("Config_Dialog", "Select folder", nullptr));
        notifyOnChange->setText(QCoreApplication::translate("Config_Dialog", "Show notifications when changing songs", nullptr));
        cbDownCover->setText(QCoreApplication::translate("Config_Dialog", "Download cover if not found locally", nullptr));
        cbSavePlaylist->setText(QCoreApplication::translate("Config_Dialog", "Save/open playlist on closing/opening", nullptr));
    } // retranslateUi

};

namespace Ui {
    class Config_Dialog: public Ui_Config_Dialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // CONFIG_UI_H
