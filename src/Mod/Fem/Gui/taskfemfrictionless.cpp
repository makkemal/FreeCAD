#include "taskfemfrictionless.h"
#include "ui_taskfemfrictionless.h"

TaskFemFrictionless::TaskFemFrictionless(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::TaskFemFrictionless)
{
    ui->setupUi(this);
}

TaskFemFrictionless::~TaskFemFrictionless()
{
    delete ui;
}
